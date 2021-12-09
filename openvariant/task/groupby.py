from collections import defaultdict
from functools import partial
from multiprocessing import Pool
from os import cpu_count
from subprocess import PIPE, Popen
from typing import Set, Generator, List, Tuple

from tqdm import tqdm

from openvariant.annotation.annotation import Annotation
from openvariant.find.find import find_files
from openvariant.utils.logger import log
from openvariant.utils.where import skip, parse_where
from openvariant.variant.variant import Variant


def _get_unique_values(file_path: str, annotation: Annotation, key: str) -> Set:
    values = set()
    result = Variant(file_path, annotation)

    try:
        for r in result.read(key):
            values.add(r[key])
    except KeyError:
        log.warn(f"'{key}' key not found in '{file_path}' file")
    return values


def group(base_path: str, annotation_path: str or None, key_by: str) -> Generator[str, List, None]:
    results = defaultdict(list)
    for file, ann in find_files(base_path, annotation_path):
        by_value = ann.annotations.get(key_by, None)

        if isinstance(by_value, tuple):
            values = _get_unique_values(file, ann, key_by)

            for s in values:
                a_clone = ann
                results[s].append((file, a_clone))

    for key, group_select in results.items():
        yield key, group_select


def _group_by_task(selection, where=None, key_by=None, script='', header=False) -> Tuple[str, List, bool]:
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
        except BrokenPipeError:
            pass
        return group_key, output, False

    else:
        process = Popen(script, shell=True, stdin=PIPE, stdout=PIPE,
                   env={"GROUP_KEY": 'None' if group_key is None else group_key})
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


def group_by(base_path: str, annotation_path: str or None, script: str or None, key_by: str, where=None,
             cores=cpu_count(), quite=False, header: bool = False) -> Generator[str, List, bool]:
    selection = list(group(base_path, annotation_path, key_by))

    with Pool(cores) as pool:
        task = partial(_group_by_task, where=where, key_by=key_by,
                       script=script, header=header)  # , where=where_parsed, columns=columns, print_headers=headers)
        map_method = map if cores == 1 or len(selection) <= 1 else pool.imap_unordered

        for group_key, group_result, command in tqdm(
                map_method(task, selection),
                total=len(selection),
                desc="Computing groups".rjust(40),
                disable=(len(selection) < 2 or quite)
        ):
            yield group_key, group_result, command
