import glob
from fnmatch import fnmatch
from os import listdir
from os.path import isfile, join, basename
from typing import Generator
from copy import deepcopy

from openvariant.annotation.annotation import Annotation, merge_annotations_structure

from openvariant.config.config_annotation import ANNOTATION_EXTENSION, DEFAULT_RECURSIVE


def _get_annotation_file(annotation: Annotation, file_name: str, file_path: str, base_path: str) -> \
        Generator[str, Annotation, None]:
    ann = None
    pattern_matches = 0
    for pattern in annotation.patterns:
        if fnmatch(file_name, pattern):
            pattern_matches += 1
            ann = deepcopy(annotation)

    # Process filename and dirname annotations
    if ann is not None and pattern_matches > 0:  # and __where_match(file_annotations, where=where):
        yield file_path, ann


def find_files(base_path: str, annotation: Annotation) -> Generator[str, Annotation, None]:
    if annotation is None or base_path is None:
        raise ValueError('Annotation or path is missing')

    global_annotation = annotation

    if isfile(base_path):
        for f, a in _get_annotation_file(global_annotation, basename(base_path), base_path, base_path):
            yield f, a

    # Find files
    else:
        try:
            for file_name in listdir(base_path):
                file_path = join(base_path, file_name)
                if isfile(file_path):
                    local_annotation = global_annotation
                    for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
                        ann = Annotation(annotation_file)
                        recursive = DEFAULT_RECURSIVE if global_annotation.recursive is None \
                            else global_annotation.recursive
                        if recursive:
                            local_annotation = merge_annotations_structure(local_annotation, ann)
                    for f, a in find_files(file_path, local_annotation):
                        yield f, a
                else:
                    # Search subfolders
                    for f, a in find_files(file_path, global_annotation):
                        yield f, a
        except PermissionError as e:
            print(e)
