import functools
from multiprocessing import Pool
from os import cpu_count
from typing import Tuple, Union, List

from tqdm import tqdm

from src.annotation.annotation import Annotation
from src.task.find import find_files
from src.utils.logger import log
from src.utils.where import parse_where, skip
from src.variant.variant import Variant


def _count_task(selection: Tuple[str, Annotation], group_by: str, where: str) -> Tuple[int, Union[dict, None]]:
    where_clauses = parse_where(where)
    i = 0
    input_file, input_annotations = selection
    result = Variant(input_file, input_annotations)

    header = result.header
    if group_by is None:
        for r in result.read():
            if skip(r, where_clauses):
                continue
            i += 1
        return i, None
    else:
        groups = {}
        # key_not_found = False
        for r in result.read():
            if skip(r, where_clauses):
                continue
            try:
                val = list(r.values())[header.index(group_by)]
                val_count = groups.get(val, 0)
                groups[val] = val_count + 1
                i += 1
            except ValueError:
                pass
                # key_not_found = True

        # if key_not_found:
        #    log.warn(f"Not found '{group_by}' key in {result.path}")

        return i, groups


def count(base_path: str, annotation_path: str, group_by=None, where=None, cores=cpu_count(), quite=False) -> \
        Tuple[int, Union[None, dict]]:
    ann = Annotation(annotation_path)

    selection = []
    for k, a in find_files(base_path, ann):
        selection += [(k, a)]

    with Pool(cores) as pool:
        groups = {}
        task = functools.partial(_count_task, group_by=group_by, where=where)
        map_method = pool.imap_unordered if len(selection) > 1 else map
        total = 0
        for c, g in tqdm(map_method(task, selection),
                         total=len(selection),
                         desc="Counting variants".rjust(40),
                         disable=(len(selection) < 2) or quite
                         ):

            # Update groups
            if g is not None:
                for k, v in g.items():
                    val = groups.get(k, 0)
                    groups[k] = val + v
            total += c

    return total, groups
