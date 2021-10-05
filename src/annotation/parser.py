from enum import Enum
from functools import partial
from os.path import basename, dirname
from typing import Tuple, Any, List, Optional, Union, Callable

from src.annotation.builder import Builder


def _get_text_by_field(x: List, line: List, original_header: List, func: Builder or None):
    value = None
    for y in x:
        value = line[original_header.index(y)] if y in original_header else None
        if value is not None:
            value = func(value) if func is not None else value
        if value is not None:
            break
    if value is None:
        return ""
    return value


def _static_parser(x: Tuple[str, Any], line: List, original_header: List, path: str) -> str:
    return x[1]


def _internal_parser(x: Tuple[str, List, Builder], line: List, original_header: List, path: str) -> \
        Optional[Union[int, str, float]]:
    return _get_text_by_field(x[1], line, original_header, x[2])


def _filename_parser(x: Tuple[str, Builder], line: List, original_header: List, path: str) -> str:
    return x[1](basename(path))


def _dirname_parser(x: Tuple[str, Builder], line: List, original_header: List, path: str) -> str:
    return x[1](basename(dirname(path)))


def _plugin_parser(x: Tuple[str, List, Callable], line: List, original_header: List, path: str) -> str:
    value = _get_text_by_field(x[1], line, original_header, None)
    return x[2](value)


class AnnotationTypesParsers(Enum):
    STATIC = partial(_static_parser)
    INTERNAL = partial(_internal_parser)
    FILENAME = partial(_filename_parser)
    DIRNAME = partial(_dirname_parser)
    PLUGIN = partial(_plugin_parser)
    '''
    MAPPING = partial(_mapping_builder)
    '''
