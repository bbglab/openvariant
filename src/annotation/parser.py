from enum import Enum
from functools import partial
from os.path import basename
from typing import Tuple, Any, List, Optional, Union, Callable


def _static_parser(x: Tuple[str, Any], line: List, original_header: List, path: str) -> str:
    return x[1]


def _internal_parser(x: Tuple[str, List], line: List, original_header: List, path: str) -> Optional[Union[int, str, float]]:
    value = None
    for y in x[1]:
        value = line[original_header.index(y)] if y in original_header else None
        if value is not None:
            break
    return value


def _filename_parser(x: Tuple[str, Callable], line: List, original_header: List, path: str) -> str:
    name = basename(path)
    return x[1](name)


class AnnotationTypesParsers(Enum):
    STATIC = partial(_static_parser)
    INTERNAL = partial(_internal_parser)
    FILENAME = partial(_filename_parser)
    '''
    DIRNAME = partial(_dirname_builder)
    
    LIFTOVER = partial(_liftover_builder)
    MAPPING = partial(_mapping_builder)
    '''
