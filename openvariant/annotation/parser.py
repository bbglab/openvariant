"""
Parser
====================================
A core Enum to get the value of each cell on the parsed file, from a specified Builder.
"""
from enum import Enum
from functools import partial
from typing import List, Tuple, Callable, Optional

from openvariant.annotation.builder import Builder
from openvariant.annotation.process import FilenameProcess, InternalProcess, StaticProcess, DirnameProcess, \
    PluginProcess, MappingProcess
from openvariant.config.config_annotation import AnnotationTypes


def _static_parser(x: StaticProcess, line: List, line_dict: dict) -> str:
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
    value = x[2](x[1])
    return value


def _internal_parser(x: InternalProcess, line: List, line_dict: dict) -> str:
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
    value = x[2](x[1]) if x[1] is None else x[2](line[x[1]])
    return value


def _filename_parser(x: FilenameProcess, line: List, line_dict: dict) -> str:
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

    value = x[2](x[1])
    return value


def _dirname_parser(x: DirnameProcess, line: List, line_dict: dict) -> str:
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

    value = x[2](x[1])
    return value


def _plugin_parser(x: PluginProcess, line: List, line_dict: dict) -> dict:
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
    value = x[2](line_dict)
    return value


def _mapping_parser(x: MappingProcess, original_header: List, line_dict: dict) -> str:
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
    value = x[2](x[1])
    return value


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
