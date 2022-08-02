import re
from fnmatch import fnmatch
from os.path import basename


def check_extension(ext: str, path: str) -> bool:
    """Check if file matches with the annotation pattern"""
    return fnmatch(basename(path), ext) if ext[0] == '*' else re.match(ext, basename(path)) is not None
