import re
from fnmatch import fnmatch


def check_extension(ext: str, path: str) -> bool:
    """Check if file matches with the annotation pattern"""
    if ext[0] == '*':
        match = fnmatch(path, ext)
    else:
        reg_apply = re.compile(ext + '$')
        match = len(reg_apply.findall(path)) != 0
    return match
