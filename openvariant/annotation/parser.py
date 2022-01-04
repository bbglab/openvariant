"""
Parser
====================================
A core Enum to get the value of each cell on the parsed file, from a specified Builder.
"""
import re
from enum import Enum
from functools import partial
from os.path import basename, dirname, abspath, isdir
from typing import List

from openvariant.annotation.builder import Builder, StaticBuilder, InternalBuilder, FilenameBuilder, DirnameBuilder, \
    PluginBuilder, MappingBuilder


def _get_text_from_header(field_sources: List, line: List, original_header: List, func: Builder or None) -> float or str:
    """Get the value of a specified field

    Parameters
    ----------
    field_sources : List
        Different fields to search for their value.
    line : List
        A row from the input file.
    original_header : List
        Header of the original input file.
    func : Builder or None
        Function to apply to the value resulted.

    Returns
    -------
    float or str
        Represents the function described on the annotation.
    """
    value = None
    for y in field_sources:
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
    """Get of a Static value

    It will return a fixed value described on the annotation file.

    Parameters
    ----------
    x : StaticBuilder
        Annotation builder.

    Returns
    -------
    str
        A value from an internal field on the input file.
    """
    return str(x[1]) if x[1] is not None else str(float('nan'))


def _internal_parser(x: InternalBuilder, line: List, original_header: List, path: str = None) -> str:
    """Get of an Internal value

    It will return an internal value of a field located in the input file.

    Parameters
    ----------
    x : InternalBuilder
        Annotation builder.
    line : List
        A row from the input file.
    original_header : List
        Header of the original input file.

    Returns
    -------
    str
        Internal value got it from input file.
    """
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
    """Get of a Filename value

    It will return a filename value apply the annotation described on the Builder.

    Parameters
    ----------
    x : FilenameBuilder
        Annotation builder.
    path : str
        Path of the input file.

    Returns
    -------
    str
        Filename value got it from the input file's path.
    """
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
    """Get of a Dirname value

    It will return a dirname value apply the annotation described on the Builder.

    Parameters
    ----------
    x : DirnameBuilder
        Annotation builder.
    path : str
        Path of the input file.

    Returns
    -------
    str
        Dirname value got it from the input file's path.
    """
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
    """Get of a Plugin value

    It will return a value applying a transformation described and implemented on the corresponding plugin.

    Parameters
    ----------
    x : PluginBuilder
        Annotation builder.
    dict_line : dict
        A row from the input file represented in a dict.

    Returns
    -------
    str
        Dirname value got it from the input file's path.
    """
    if x[1] is None:
        raise KeyError("Unable to get plugin\'s function")
    if dict_line is None:
        dict_line = {}
    try:
        value = x[1](dict_line)
    except Exception as e:
        raise Exception(f'Something went wrong on the plugin: {e}')

    #if len(x[1]) != 0:
    #    value = _get_text_from_header(x[1], line, original_header, None)
    return value if value is not None else str(float('nan'))


def _mapping_parser(x: MappingBuilder, line: List = None, original_header: List = None, path: str = None, dict_line: dict = None) \
        -> str:
    """Get of a Mapping value

    It will return a value of mapping annotation. Looking for the proper field on the mapping file and matching with the
    value of the input file, it will return the value described on the annotation file.

    Parameters
    ----------
    x : MappingBuilder
        Annotation builder.
    line : List
        A row from the input file.
    original_header : List
        Header of the original input file.
    dict_line : dict
        A row from the input file represented in a dict.

    Returns
    -------
    str
        Dirname value got it from the input file's path.
    """
    if x[1] is None or x[2] is None or line is None or original_header is None or dict_line is None:
        raise ValueError('Unable to make mapping.')
    value = None
    for field in x[1]:
        if value is None:
            try:
                k = dict_line[field]
                value = x[2][k]
            except KeyError:
                pass
        if value is not None:
            break

    return str(value) if value is not None else str(float('nan'))


class AnnotationTypesParsers(Enum):
    """Enum to get the value of every annotation Builder"""

    """Parser for static builder"""
    STATIC = partial(_static_parser)

    """Parser for internal builder"""
    INTERNAL = partial(_internal_parser)

    """Parser for filename builder"""
    FILENAME = partial(_filename_parser)

    """Parser for dirname builder"""
    DIRNAME = partial(_dirname_parser)

    """Parser for plugin builder"""
    PLUGIN = partial(_plugin_parser)

    """Parser for mapping builder"""
    MAPPING = partial(_mapping_parser)
