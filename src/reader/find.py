import glob

from os.path import isfile, join, dirname

from src.annotation.annotation import Annotation

from src.config.config_annotation import ANNOTATION_EXTENSION


def __merge_annotations(a, b):
    """

    :param a: The first annotations dictionary
    :param b: The second annotations dictionary. This annotations have preference and will override A annotations if there is a conflict
    :return: The union of A and B annotation dictionaries
    """

    # Clone A
    c = {k: dict(v) for k, v in a.items()}

    # Update or add B entries
    for k, v in b.items():
        if k in c:

            # Update the annotations
            for kv, vv in v.items():
                if kv not in c[k]:
                    c[k][kv] = vv
                else:
                    if isinstance(c[k][kv], list):
                        # If it's a list concat them instead of override it
                        vv_list = vv if isinstance(vv, list) else [vv]
                        c[k][kv] = list(c[k][kv]) + vv_list
                    else:
                        # Override the value
                        c[k][kv] = vv

        else:
            c[k] = {k: v for k, v in c['global'].items()} if 'global' in c else {}
            c[k].update(v)

    return c


def __sub_find_files(base_path: str, annotations=None):
    global_annotations = {} if annotations is None else annotations

    if isfile(base_path):
        yield base_path, global_annotations
        return

    local_annotations = {}
    for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
        annotation = Annotation(annotation_file)
        ann = annotation.structure
        print(ann)
        '''
        if annotation.recursive:
            global_annotations = __merge_annotations(global_annotations, ann)
        else:
            local_annotations = __merge_annotations(local_annotations, ann)
        '''

    return base_path, global_annotations


def find_files(base_path: str):
    return __sub_find_files(base_path)
