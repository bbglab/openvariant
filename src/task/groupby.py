from collections import defaultdict

from src.annotation.annotation import Annotation
from src.config.config_annotation import AnnotationTypes
from src.task.find import find_files
from src.utils.logger import log
from src.variant.variant import Variant


def _get_unique_values(file_path, annotation, key):
    values = set()
    result = Variant(file_path, annotation)
    header = result.header
    try:
        pos = header.index(key)
    except (IndexError, ValueError):
        pos = None

    if pos is not None:
        for r in result.generator:
            values.add(r[pos])
    return values


def sub_group_by(base_path: str, annotation: Annotation, key_by: str, where=None):
    results = defaultdict(list)
    for file, ann in find_files(base_path, annotation):
        by_value = ann.annotations.get(key_by, None)

        if isinstance(by_value, tuple):
            if by_value[0] == AnnotationTypes.INTERNAL.name:
                values = _get_unique_values(file, ann, key_by)

                for s in values:
                    a_clone = dict(ann.annotations)
                    a_clone[key_by] = (key_by, s, {s})
                    results[s].append((file, a_clone))

    # print(results)
    for key, group in results.items():
        yield key, group


def group_by(selection):
    group_key, group_values = selection
    print(group_values)
    # try:
    #    for r in readers.variants(group_values):

    #        # TODO Implement where using annotations
    #        if __skip(r, where):
    #            continue

    #        process.stdin.write("{}\n".format("\t".join([str(r.get(h, "")) for h in headers])).encode())
    #        process.stdin.flush()
    #    process.stdin.close()
    # except BrokenPipeError:
    #    pass

    # output = []
    # try:
    #    while True:
    #        out = process.stdout.readline().decode().strip()
    #        if out == "":
    #            break
    #        output.append(out)
    #    process.stdout.close()
    # except BrokenPipeError:
    #    pass

    # return group_key, output
