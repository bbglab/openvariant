import re
from enum import Enum
from functools import partial
from os.path import basename, dirname, abspath
from typing import Tuple, Any, List, Optional, Union, Callable

from openvariant.annotation.builder import Builder


def _get_text_from_header(x: List, line: List, original_header: List, func: Builder or None):
    value = None
    for y in x:
        value = line[original_header.index(y)] if y in original_header else None
        try:
            value = func(value) if func is not None else value
        except AttributeError:
            value = None
        if value is not None:
            break
    if value is None:
        return float('nan')
    return value


def _static_parser(x: Tuple[str, Any], line: List, original_header: List, path: str) -> str:
    return x[1]


def _internal_parser(x: Tuple[str, List, Builder, str], line: List, original_header: List, path: str) -> \
        Optional[Union[int, str, float]]:
    for y in x[1]:
        if isinstance(y, list):
            dict_field = {}
            for field in y:
                value = line[original_header.index(field)] if field in original_header else None
                if value is not None:
                    dict_field[field] = value
                    continue
                if value is None:
                    dict_field[field] = str(float('nan'))
            try:
                return x[3].format(**dict_field)
            except KeyError:
                continue
        if isinstance(y, str):
            return _get_text_from_header(x[1], line, original_header, x[2])

    return float('nan')


def _filename_parser(x: Tuple[str, Builder, re.Pattern], line: List, original_header: List, path: str) -> str:
    func_result = x[1](basename(path))
    value = x[2].findall(func_result)[0]
    return value if value is not None else float('nan')


def _dirname_parser(x: Tuple[str, Builder, re.Pattern], line: List, original_header: List, path: str) -> str:
    func_result = x[1](basename(dirname(abspath(path))))
    value = x[2].findall(func_result)[0]
    return value if value is not None else float('nan')


def _plugin_parser(x: Tuple[str, List, Callable], line: List, original_header: List, path: str) -> str:
    value = _get_text_from_header(x[1], line, original_header, None)
    value = x[2](value)
    return value if value is not None else float('nan')


def _mapping_parser(x: Tuple[str, List, dict], line: List, original_header: List, path: str, dict_line: dict) \
        -> str or float:
    value = None
    for field in x[1]:
        value = line[original_header.index(field)] if field in original_header else None
        if value is None:
            try:
                k = dict_line[field]
                value = x[2][k]
            except KeyError:
                pass
                #raise KeyError(f"Enable to found '{field}' in the mapping file.")
        if value is not None:
            break

    return value if value is not None else str(float('nan'))


class AnnotationTypesParsers(Enum):
    STATIC = partial(_static_parser)
    INTERNAL = partial(_internal_parser)
    FILENAME = partial(_filename_parser)
    DIRNAME = partial(_dirname_parser)
    PLUGIN = partial(_plugin_parser)
    MAPPING = partial(_mapping_parser)
