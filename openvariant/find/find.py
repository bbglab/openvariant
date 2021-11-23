import glob
from fnmatch import fnmatch
from os import listdir
from os.path import isfile, join, basename, abspath, dirname
from typing import Generator
from copy import deepcopy

from openvariant.annotation.annotation import Annotation

from openvariant.config.config_annotation import ANNOTATION_EXTENSION


def _get_annotation_file(annotation: Annotation or None, file_name: str, file_path: str, base_path: str) -> \
        Generator[str, Annotation, None]:
    if annotation is None:
        for annotation_file in glob.iglob(join(dirname(abspath(base_path)), "*.{}".format(ANNOTATION_EXTENSION))):
            annotation = Annotation(annotation_file)

    ann = None
    pattern_matches = 0
    if annotation is not None:
        for pattern in annotation.patterns:
            if fnmatch(file_name, pattern):
                pattern_matches += 1
                ann = deepcopy(annotation)

    # Process filename and dirname annotations
    if ann is not None and pattern_matches > 0:  # and __where_match(file_annotations, where=where):
        yield file_path, ann


def _find_files(base_path: str, annotation: Annotation or None, fix: bool) -> Generator[str, Annotation, None]:

    if isfile(base_path):
        for f, a in _get_annotation_file(annotation, basename(base_path), base_path, base_path):
            yield f, a

    # Find files
    else:
        try:
            for file_name in listdir(base_path):
                file_path = join(base_path, file_name)
                if isfile(file_path):
                    # local_annotation = global_annotation
                    if not fix:
                        for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
                            annotation = Annotation(annotation_file)
                            # recursive = DEFAULT_RECURSIVE if global_annotation.recursive is None \
                            #    else global_annotation.recursive
                            # if recursive:
                            #    local_annotation = merge_annotations_structure(local_annotation, ann)
                    for f, a in _find_files(file_path, annotation, fix):
                        yield f, a
                else:
                    for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
                        annotation = Annotation(annotation_file)
                    # Search subfolders
                    for f, a in _find_files(file_path, annotation, fix):
                        yield f, a
        except PermissionError as e:
            print(e)


def find_files(base_path: str, annotation_path: str or None = None) -> Generator[str, Annotation, None]:
    annotation, fix = (Annotation(annotation_path), True) if annotation_path is not None else (None, False)
    return _find_files(base_path, annotation, fix)
