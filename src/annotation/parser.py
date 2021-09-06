from enum import Enum
from functools import partial
from os.path import basename, dirname, normpath
from typing import Tuple, Any, List, Optional, Union, Callable

from pyliftover import LiftOver
from liftover import get_lifter


def _static_parser(x: Tuple[str, Any], line: List, original_header: List, path: str) -> str:
    return x[1]


def _internal_parser(x: Tuple[str, List], line: List, original_header: List, path: str) -> \
        Optional[Union[int, str, float]]:
    value = None
    for y in x[1]:
        value = line[original_header.index(y)] if y in original_header else None
        if value is not None:
            break
    if value is None:
        return ""
    return value


def _filename_parser(x: Tuple[str, str], line: List, original_header: List, path: str) -> str:
    return x[1]


def _dirname_parser(x: Tuple[str, str], line: List, original_header: List, path: str) -> str:
    return x[1]


def _liftover_parser(x: Tuple[str, str, str, str], line: List, original_header: List, path: str) -> str:
    value = None
    for y in x[3]:
        value = line[original_header.index(y)] if y in original_header else None
        if value is not None:
            break
    # lo = LiftOver(x[1], x[2])
    lo = get_lifter(x[1].lower(), x[2].lower())
    if not str(value).startswith("chr"):
        try:
            result = lo[value, 1000000]
        except KeyError as e:
            result = None
        # lo.convert_coordinate("chr" + str(value), 1000000)
    else:
        try:
            result = lo[value[3:], 1000000]
        except KeyError as e:
            result = None
        # result = lo.convert_coordinate(value, 1000000)
    if result is None:
        return ""
    return result[0][3]


class AnnotationTypesParsers(Enum):
    STATIC = partial(_static_parser)
    INTERNAL = partial(_internal_parser)
    FILENAME = partial(_filename_parser)
    DIRNAME = partial(_dirname_parser)
    LIFTOVER = partial(_liftover_parser)
    '''
    MAPPING = partial(_mapping_builder)
    '''
