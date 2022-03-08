"""
Find
====================================
A core functionally to search files and with its corresponding annotation.
"""
import glob
import re
from fnmatch import fnmatch
from os import listdir
from os.path import isfile, join, basename, abspath, dirname
from typing import Generator
from copy import deepcopy

from openvariant.annotation.annotation import Annotation

from openvariant.config.config_annotation import ANNOTATION_EXTENSION


def _check_extension(ext: str, path: str) -> bool:
    """Check if file matches with the annotation pattern"""
    if ext[0] == '*':
        match = fnmatch(path, ext)
    else:
        reg_apply = re.compile(ext + '$')
        match = len(reg_apply.findall(path)) != 0
    return match


def _find_files(base_path: str, annotation: Annotation or None, fix: bool) -> Generator[str, Annotation, None]:
    """Recursive exploration from a base path"""
    if not fix:
        for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
            annotation = Annotation(annotation_file)

    for file_name in listdir(base_path):
        try:
            file_path = join(base_path, file_name)

            if isfile(file_path):
                if annotation is not None:
                    try:
                        for ext, _ in annotation.structure.items():
                            if _check_extension(ext, file_path):
                                yield file_path, annotation
                    except AttributeError:
                        raise AttributeError("Unable to parse annotation file, check its location.")
            else:
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
