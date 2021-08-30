from os import listdir
from os.path import isfile, join
import re
from typing import Generator

from src.annotation.annotation import Annotation
from src.unify.parser import parser


def _check_extension(ext: str, path: str) -> re.Match:
    rext = re.compile(ext + "$")
    return rext.search(path)


def unify(base_path: str, annotation: Annotation) -> Generator[str, None, None]:
    an = annotation.structure
    format_output = annotation.format
    if isfile(base_path):
        for ext, ann in an.items():
            if _check_extension(ext, base_path):
                for x in parser(base_path, ann, format_output):
                    yield x

    try:
        for file in listdir(base_path):
            file_path = join(base_path, file)
            if isfile(file_path):
                for ext, ann in an.items():
                    if _check_extension(ext, file_path):
                        for x in parser(file_path, ann, format_output):
                            yield x
            else:
                for x in unify(file_path, annotation):
                    yield x
    except PermissionError as e:
        print(e)
