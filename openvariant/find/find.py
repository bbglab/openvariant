"""
Find
====================================
A core functionally to search files and with its corresponding annotation.
"""
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
    """Get Annotation object from file location or inherits Annotation of parent directory"""
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
    """Recursive exploration from a base path"""
    if isfile(base_path):
        for f, a in _get_annotation_file(annotation, basename(base_path), base_path, base_path):
            yield f, a

    # Find files
    else:
        for file_name in listdir(base_path):
            try:
                file_path = join(base_path, file_name)
                if isfile(file_path):
                    if not fix:
                        for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
                            annotation = Annotation(annotation_file)
                    for f, a in _find_files(file_path, annotation, fix):
                        yield f, a
                else:
                    for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
                        annotation = Annotation(annotation_file)
                    # Search subfolders
                    for f, a in _find_files(file_path, annotation, fix):
                        yield f, a
            except PermissionError as e:
                raise PermissionError(f"Unable to open {file_name}: {e}")


def find_files(base_path: str, annotation_path: str or None = None) -> Generator[str, Annotation, None]:
    """Get each file and its proper annotation object.

    Parameters
    ----------
    base_path : srt
        Base path of input files.
    annotation_path : str or None
        Path of annotation file.

    Yields
    -------
    str
        Input file's name.
    Annotation
        The proper schema of each input file.
    """
    annotation, fix = (Annotation(annotation_path), True) if annotation_path is not None else (None, False)
    return _find_files(base_path, annotation, fix)
