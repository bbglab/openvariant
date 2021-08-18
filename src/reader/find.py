import glob
from fnmatch import fnmatch
from os import listdir
from os.path import isfile, join

from src.annotation.annotation import Annotation, merge_annotations_structure, process_annotations

from src.config.config_annotation import ANNOTATION_EXTENSION


def __sub_find_files(base_path: str, annotations=None):
    global_annotations = {} if annotations is None else annotations

    if isfile(base_path):
        yield base_path, global_annotations

    local_annotations = {}
    for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
        annotation = Annotation(annotation_file)
        ann = annotation.structure
        if annotation.recursive:
            global_annotations = merge_annotations_structure(global_annotations, ann)
        else:
            local_annotations = merge_annotations_structure(local_annotations, ann)

    # Merge local and global annotations, but local have preference over global
    local_annotations = merge_annotations_structure(global_annotations, local_annotations)

    # Find files
    try:
        for file in listdir(base_path):
            file_path = join(base_path, file)
            if isfile(file_path):
                file_annotations = {}
                pattern_matches = 0
                for pattern, annotations in local_annotations.items():
                    if fnmatch(file_path, pattern):
                        pattern_matches += 1
                        file_annotations.update(annotations)
                # Process filename annotations
                file_annotations = process_annotations(file_annotations, base_path, file)

                if pattern_matches > 0:  # and __where_match(file_annotations, where=where):
                    yield file_path, file_annotations

            else:
                # Search subfolders
                for f, a in __sub_find_files(file_path, global_annotations):
                    yield f, a
    except PermissionError as e:
        print(e)


def find_files(base_path: str):
    return __sub_find_files(base_path)



