from collections import defaultdict
from functools import partial
from multiprocessing import Pool
from os import cpu_count
from subprocess import Popen, PIPE

from tqdm import tqdm

from src.annotation.annotation import Annotation
from src.task.find import find_files
from src.utils.logger import log
from src.variant.variant import Variant


def _get_unique_values(file_path, annotation, key):
    values = set()
    result = Variant(file_path, annotation)

    try:
        for r in result.read():
            values.add(r[key])
    except KeyError:
        log.warn(f"'{key}' key not found in '{file_path}' file")
    return values


def sub_group_by(base_path: str, annotation: Annotation, key_by: str, where=None):
    results = defaultdict(list)
    for file, ann in find_files(base_path, annotation):
        by_value = ann.annotations.get(key_by, None)

        if isinstance(by_value, tuple):
            values = _get_unique_values(file, ann, key_by)

            for s in values:
                a_clone = ann
                # a_clone[key_by] = (key_by, s, {s})
                results[s].append((file, a_clone))

    for key, group in results.items():
        yield key, group


def group_by_task(selection):
    group_key, group_values = selection
    output = []
    try:
        for value in group_values:
            result = Variant(value[0], value[1])
            for row in result.read():
                output.append(list(row.values()))
    except BrokenPipeError:
        pass
    return group_key, output


def group_by(base_path: str, annotation: Annotation, key_by: str, cores=cpu_count(), where=None):
    selection = list(sub_group_by(base_path, annotation, key_by))

    with Pool(cores) as pool:
        task = partial(group_by_task)  # script=script, where=where_parsed, columns=columns, print_headers=headers)
        map_method = map if cores == 1 or len(selection) <= 1 else pool.imap_unordered

        for group_key, group_result in tqdm(
                map_method(task, selection),
                total=len(selection),
                desc="Computing groups".rjust(40),
                disable=(len(selection) < 2)  # or quite)
        ):
            yield group_key, group_result
