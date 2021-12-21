import re
from enum import Enum
from functools import partial
from os.path import basename, dirname, abspath, isfile, isdir
from typing import List

from openvariant.annotation.builder import Builder, StaticBuilder, InternalBuilder, FilenameBuilder, DirnameBuilder, \
    PluginBuilder, MappingBuilder


def _get_text_from_header(x: List, line: List, original_header: List, func: Builder or None) -> float or str:
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


def _static_parser(x: StaticBuilder, line: List = None, original_header: List = None, path: str = None) -> str:
    return str(x[1]) if x[1] is not None else str(float('nan'))


def _internal_parser(x: InternalBuilder, line: List = None, original_header: List = None, path: str = None) -> str:
    try:
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
                    return str(x[3].format(**dict_field))
                except KeyError:
                    continue
            if isinstance(y, str):
                return str(_get_text_from_header(x[1], line, original_header, x[2]))
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')
    except SyntaxError:
        raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')

    return str(float('nan'))


def _filename_parser(x: FilenameBuilder, line: List = None, original_header: List = None, path: str = None) -> str:

    try:
        if isdir(path):
            raise FileNotFoundError('Unable to find a filename')

        func_result = x[1](basename(path))
        value = x[2].findall(func_result)[0]
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')
    except SyntaxError:
        raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')
    except (re.error, IndexError):
        raise re.error(f'Wrong regex pattern on {x[0]} annotation')

    return str(value) if value is not None else str(float('nan'))


def _dirname_parser(x: DirnameBuilder, line: List = None, original_header: List = None, path: str = None) -> str:
    try:
        if isdir(path):
            raise FileNotFoundError('Unable to find a dirname')

        func_result = x[1](basename(dirname(abspath(path))))
        value = x[2].findall(func_result)[0]
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')
    except SyntaxError:
        raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')
    except (re.error, IndexError):
        raise re.error(f'Wrong regex pattern on {x[0]} annotation')

    return str(value) if value is not None else str(float('nan'))


def _plugin_parser(x: PluginBuilder, line: List = None, original_header: List = None, path: str = None,
                   dict_line: dict = None) -> dict:
    if x[2] is None:
        raise KeyError("Unable to get plugin\'s function")
    if dict_line is None:
        dict_line = {}
    try:
        value = x[2](dict_line)
    except Exception as e:
        raise Exception(f'Something went wrong on the plugin: {e}')

    #if len(x[1]) != 0:
    #    value = _get_text_from_header(x[1], line, original_header, None)
    return value if value is not None else str(float('nan'))


def _mapping_parser(x: MappingBuilder, line: List = None, original_header: List = None, path: str = None, dict_line: dict = None) \
        -> str:
    if x[1] is None or x[2] is None or line is None or original_header is None or dict_line is None:
        raise ValueError('Unable to make mapping.')
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

    return str(value) if value is not None else str(float('nan'))


class AnnotationTypesParsers(Enum):
    STATIC = partial(_static_parser)
    INTERNAL = partial(_internal_parser)
    FILENAME = partial(_filename_parser)
    DIRNAME = partial(_dirname_parser)
    PLUGIN = partial(_plugin_parser)
    MAPPING = partial(_mapping_parser)
