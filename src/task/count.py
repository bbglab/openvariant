import functools
from multiprocessing import Pool
from os import cpu_count

from tqdm import tqdm

from src.annotation.annotation import Annotation
from src.task.find import find_files
from src.variant.variant import Variant


def count_task(selection):
    i = 0
    input_file, input_annotations = selection
    result = Variant(input_file, input_annotations)
    for _ in result.read(False):
        i += 1
    return i, None


def count(annotation_path: str, base_path: str):
    ann = Annotation(annotation_path)

    selection = []
    for k, a in find_files(base_path, ann):
        selection += [(k, a)]

    with Pool(cpu_count()) as pool:
        task = functools.partial(count_task)
        map_method = pool.imap_unordered if len(selection) > 1 else map
        total = 0
        for c, g in tqdm(map_method(task, selection),
                         total=len(selection),
                         desc="Counting variants".rjust(40),
                         disable=(len(selection) < 2)
                         ):
            total += c
    print(total)
