"""
Find files
====================================
A core functionally to search files and with its corresponding annotation.
"""
import glob
from os import listdir
from os.path import isfile, join, isdir, dirname
from typing import Generator
import warnings

from openvariant.annotation.annotation import Annotation
from openvariant.annotation.config_annotation import ANNOTATION_EXTENSION
from openvariant.utils.utils import check_extension


def _get_annotation(file_path, annotation):
    if annotation is not None:
        try:
            for ext, _ in annotation.structure.items():
                if check_extension(ext, file_path):
                    yield file_path, annotation
        except AttributeError:
            raise AttributeError("Unable to parse annotation file, check its location.")


def _scan_files(base_path: str, annotation: Annotation, fix: bool, skip_files: bool):
    """Recursive exploration from a base path"""
    if isdir(base_path):
        if not fix:
            for annotation_file in glob.iglob(join(base_path, "*.{}".format(ANNOTATION_EXTENSION))):
                annotation = Annotation(annotation_file)
        list_files = listdir(base_path)
        list_files.sort()
        for file_name in list_files:
            file_path = join(base_path, file_name)
            try:
                for f, a in _scan_files(file_path, annotation, fix, skip_files):
                    yield f, a
            except PermissionError:
                if skip_files:
                    warnings.warn(f"Permission denied on {file_path}", UserWarning)
                else:
                    raise PermissionError(f"Permission denied on {file_path}")
    elif isfile(base_path):
        file_path = base_path
        try:
            for f, a in _get_annotation(file_path, annotation):
                yield f, a
        except PermissionError:
            if skip_files:
                warnings.warn(f"Permission denied on {file_path}", UserWarning)
            else:
                raise PermissionError(f"Permission denied on {file_path}")
    else:
        if skip_files:
            warnings.warn(f"Unable to open {base_path}, it is neither a file nor a directory, or it does not exist.", UserWarning)
        else:
            raise FileNotFoundError(f"Unable to open {base_path}, it is neither a file nor a directory, or it does not exist.")



def _find_files(base_path: str, annotation: Annotation or None, fix: bool, skip_files: bool) -> Generator[str, Annotation, None]:
    """Recursive exploration from a base path distinct if there's a fix annotation or no"""
    if not fix:
        if isfile(base_path):
            annotation_path = dirname(base_path)
        else:
            annotation_path = base_path
        for annotation_file in glob.iglob(join(annotation_path, "*.{}".format(ANNOTATION_EXTENSION))):
            annotation = Annotation(annotation_file)
            
    for f, a in _scan_files(base_path, annotation, fix, skip_files):
        yield f, a


def findfiles(base_path: str, annotation_path: str or None = None, skip_files: bool = False) -> Generator[str, Annotation, None]:
    """Get each file and its proper annotation object.

    Parameters
    ----------
    base_path : srt
        Base path of input folder/file.
    annotation_path : str or None
        Path of annotation file.
    skip_files : bool
        Skip unreadable files and directories.

    Yields
    -------
    str
        Input file's name.
    Annotation
        The proper schema of each input file.
    """
    annotation, fix = (Annotation(annotation_path), True) if annotation_path is not None else (None, False)
    for f, a in _find_files(base_path, annotation, fix, skip_files):
        yield f, a