"""
Count  task
====================================
A core functionality to execute count task.
"""
from functools import partial
from multiprocessing import Pool
from os import cpu_count
from typing import Tuple, Union

from tqdm import tqdm

from openvariant.annotation.annotation import Annotation
from openvariant.find_files.find_files import findfiles

from openvariant.variant.variant import Variant


def _count_task(selection: [str, str], group_by: str, where: str, skip_files: bool) -> Tuple[int, Union[dict, None]]:
    """Main functionality for count task"""

    i = 0
    input_file, input_annotations = selection
    annotation = Annotation(input_annotations)
    result = Variant(input_file, annotation, skip_files)

    if group_by is None:
        for _ in result.read(where=where):
            i += 1
        return i, None
    else:
        groups = {}
        for r in result.read(where=where, group_key=group_by):
            try:
                val = r[group_by]
                val_count = groups.get(val, 0)
                groups[val] = val_count + 1
                i += 1
            except (ValueError, KeyError):
                pass
        return i, groups


def count(base_path: str, annotation_path: str or None, group_by: str = None, where: str = None,
          cores: int = cpu_count(), quite: bool = False, skip_files: bool = False) -> Tuple[int, Union[None, dict]]:
    """Print on the stdout the count result.

    It'll parse the input files with its proper annotation schema, and it'll show the count result on the stdout.
    Can be grouped by a field and can be added a 'where' expression.

    Parameters
    ----------
    base_path : srt
        Base path of input files.
    annotation_path : str or None
        Path of annotation file.
    group_by : str
        Field to group the result.
    where : str
        Conditional statement.
    quite : bool
        Discard progress bar.
    cores : int
        Number of cores to parallelize the task.
    skip_files : bool
        Skip unreadable files and directories.

    Returns
    ----------
    int
        The total number of rows.
    dict
        A schema with separate groups and the numbers of rows for each.
    """
    selection = []
    for k, a in findfiles(base_path, annotation_path):
        selection += [(k, a.path)]

    with Pool(cores) as pool:
        groups = {}
        task = partial(_count_task, group_by=group_by, where=where, skip_files=skip_files)
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
