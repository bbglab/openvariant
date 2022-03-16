"""
Group by task
====================================
A core functionality to execute group by task.
"""
from collections import defaultdict
from functools import partial
from multiprocessing import Pool
from os import cpu_count
from subprocess import PIPE, Popen
from typing import Generator, List, Tuple

from tqdm import tqdm

from openvariant.annotation.annotation import Annotation
from openvariant.find.find import find_files
from openvariant.utils.logger import log
from openvariant.utils.where import skip, parse_where
from openvariant.variant.variant import Variant


def _get_unique_values(file_path: str, annotation: Annotation, key: str) -> Tuple[set, List]:
    """Get unique values of the group by field"""
    values = set()
    result = Variant(file_path, annotation)
    result_read = []
    try:
        for r in result.read(key):
            values.add(r[key])
            result_read.append(r)
    except KeyError:
        log.warn(f"'{key}' key not found in '{file_path}' file")
    return values, result_read


def _group(base_path: str, annotation_path: str or None, key_by: str) -> List[Tuple[str, List]]:
    """Group file and its annotation by the group value"""
    results = defaultdict(list)
    for file, ann in find_files(base_path, annotation_path):
        by_value = ann.annotations.get(key_by, None)

        if isinstance(by_value, tuple):
            values, result_read = _get_unique_values(file, ann, key_by)
            for s in values:
                results[s].append((file, ann))

    results_by_groups = []
    for key, group_select in results.items():
        results_by_groups.append((key, group_select))
    return results_by_groups


def _group_by_task(selection, where=None, key_by=None, script='', header=False) -> Tuple[str, List, bool]:
    """Main functionality for group by task"""
    where_clauses = parse_where(where)
    group_key, group_values = selection

    output = []
    if script is None:
        try:
            for value in group_values:
                result = Variant(value[0], value[1])

                columns = result.annotation.columns if len(result.annotation.columns) != 0 else result.header
                if header:
                    line = "\t".join([str(h).strip() for h in columns])
                    output.append(f"{line}")
                    header = False

                for row in result.read(key_by):

                    if skip(row, where_clauses):
                        continue

                    if row[key_by] == group_key:
                        line = "\t".join([str(row[h]).strip() for h in columns])
                        output.append(f"{line}")
                    # break
        except BrokenPipeError:
            pass
        return group_key, output, False

    else:
        try:
            process = Popen(script, shell=True, stdin=PIPE, stdout=PIPE,
                            env={"GROUP_KEY": 'None' if group_key is None else group_key})
        except ProcessLookupError as e:
            raise ChildProcessError(f"Unable to run '{script}': {e}")
        try:
            for value in group_values:
                result = Variant(value[0], value[1])
                columns = result.annotation.columns if len(result.annotation.columns) != 0 else result.header

                if header:
                    line = "\t".join([str(h).strip() for h in columns])
                    process.stdin.write(f"{line}\n".encode())
                    process.stdin.flush()
                    header = False
                for row in result.read(key_by):
                    if skip(row, where_clauses):
                        continue
                    try:
                        if row[key_by] == group_key:
                            line = "\t".join([str(row[h]).strip() for h in columns])
                            process.stdin.write(f"{line}\n".encode())
                            process.stdin.flush()
                    except KeyError:
                        pass
            process.stdin.close()
        except BrokenPipeError:
            pass

        try:
            while True:
                out = process.stdout.readline().decode().strip()
                if out == "":
                    break
                output.append(out)
            process.stdout.close()
        except BrokenPipeError:
            pass
        return group_key, output, True


def group_by(base_path: str, annotation_path: str or None, script: str or None, key_by: str, where: str or None = None,
             cores=cpu_count(), quite=False, header: bool = False) -> Generator[Tuple[str, List, bool], None, None]:
    """Print on the stdout the group by result.

    It'll parse the input files with its proper annotation schema, and it'll show the parsed result separated for each
    group by value. It'll be grouped by a field and can be added a 'where' expression. Also, the result can be
    executed thought a bash script.

    Parameters
    ----------
    base_path : srt
        Base path of input files.
    annotation_path : str or None
        Path of annotation file.
    script : str or None
        Path of annotation file.
    key_by : str
        Field to group the result.
    where : str
        Conditional statement.
    quite : bool
        Discard progress bar.
    cores : int
        Number of cores to parallelize the task.
    header : bool
        Number of cores to parallelize the task.
    Returns
    ----------
    int
        The total number of rows.
    dict
        A schema with separate groups and the numbers of rows for each.
    """
    selection = _group(base_path, annotation_path, key_by)
    with Pool(cores) as pool:
        task = partial(_group_by_task, where=where, key_by=key_by, script=script, header=header)
        map_method = map if cores == 1 or len(selection) <= 1 else pool.imap_unordered

        for group_key, group_result, command in tqdm(
                map_method(task, selection),
                total=len(selection),
                desc="Computing groups".rjust(40),
                disable=(len(selection) < 2 or quite)
        ):
            yield group_key, group_result, command
