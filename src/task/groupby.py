from collections import defaultdict
from functools import partial
from multiprocessing import Pool
from os import cpu_count
from typing import Set, Generator, List, Tuple

from tqdm import tqdm

from src.annotation.annotation import Annotation
from src.task.find import find_files
from src.utils.logger import log
from src.utils.where import skip, parse_where
from src.variant.variant import Variant


def _get_unique_values(file_path, annotation, key) -> Set:
    values = set()
    result = Variant(file_path, annotation)

    try:
        for r in result.read():
            values.add(r[key])
    except KeyError:
        log.warn(f"'{key}' key not found in '{file_path}' file")
    return values


def group(base_path: str, annotation: Annotation, key_by: str) -> Generator[str, List, None]:
    results = defaultdict(list)
    for file, ann in find_files(base_path, annotation):
        by_value = ann.annotations.get(key_by, None)

        if isinstance(by_value, tuple):
            values = _get_unique_values(file, ann, key_by)

            for s in values:
                a_clone = ann
                results[s].append((file, a_clone))

    for key, group_select in results.items():
        yield key, group_select


def group_by_task(selection, where=None) -> Tuple[str, List]:
    where_clauses = parse_where(where)
    group_key, group_values = selection
    output = []
    try:
        for value in group_values:
            result = Variant(value[0], value[1])
            for row in result.read():
                if skip(row, where_clauses):
                    continue
                output.append(list(row.values()))
    except BrokenPipeError:
        pass
    return group_key, output


def group_by(base_path: str, annotation_path: str, key_by: str, where=None, cores=cpu_count(), quite=False) -> \
        Generator[str, List, None]:
    annotation = Annotation(annotation_path)
    selection = list(group(base_path, annotation, key_by))

    with Pool(cores) as pool:
        task = partial(group_by_task, where=where)  # script=script, where=where_parsed, columns=columns, print_headers=headers)
        map_method = map if cores == 1 or len(selection) <= 1 else pool.imap_unordered

        for group_key, group_result in tqdm(
                map_method(task, selection),
                total=len(selection),
                desc="Computing groups".rjust(40),
                disable=(len(selection) < 2 or quite)
        ):
            yield group_key, group_result
