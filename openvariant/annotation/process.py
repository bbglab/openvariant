import re
from enum import Enum
from functools import partial
from os.path import isdir, basename, abspath, dirname
from typing import Tuple, List, Callable, Optional

from openvariant.annotation.builder import StaticBuilder, InternalBuilder, FilenameBuilder, Builder, DirnameBuilder, \
    PluginBuilder, MappingBuilder
from openvariant.config.config_annotation import AnnotationTypes
from openvariant.plugins.context import Context

StaticProcess = Tuple[str, float or int or str, Callable]
InternalProcess = Tuple[str, Optional[int], Callable]
FilenameProcess = Tuple[str, float or int or str, Callable]
DirnameProcess = Tuple[str, float or int or str, Callable]
PluginProcess = Tuple[str, Context, Callable]
MappingProcess = Tuple[str, MappingBuilder, Callable]


def _static_process(x: StaticBuilder, original_header: List = [] or None, file_path: str = None,
                    annotation: dict = None) \
        -> StaticProcess:
    """Get a Static value
    It will return a StaticProcess describing the value to get from static annotation.
    Parameters
    ----------
    x : StaticBuilder
        Annotation builder.
    Returns
    -------
    str
        Annotation type
    float or int or str
        Fixed value
    Callable
        Function to execute on the fixed value
    """
    try:
        return AnnotationTypes.STATIC.name, x[1] if x[1] is not None else float('nan'), str
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')


def _internal_process(x: InternalBuilder, original_header: List = [] or None, file_path: str = None,
                      annotation: dict = None) \
        -> InternalProcess:
    """Get an Internal value
    It will return a InternalProcess describing the value to get from internal annotation.
    Parameters
    ----------
    x : InternalBuilder
        Annotation builder.
    Returns
    -------
    str
        Annotation type
    float or int or str
        Fixed value
    Callable
        Function to execute on the fixed value
    """
    field_pos = None
    try:
        for i, h in enumerate(original_header):
            if h in set(x[1]):
                field_pos = i
                break
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')
    except SyntaxError:
        raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')

    return AnnotationTypes.INTERNAL.name, field_pos, x[2]


def _filename_process(x: FilenameBuilder, original_header: List = [] or None, file_path: str = None,
                      annotation: dict = None) \
        -> FilenameProcess:
    """Get a Filename value
    It will return a FilenameProcess describing the value to get from filename annotation.
    Parameters
    ----------
    x : FilenameBuilder
        Annotation builder
    file_path: str
        Path of input file
    Returns
    -------
    str
        Annotation type
    float or int or str
        Fixed value
    Callable
        Function to execute on the fixed value
    """
    try:
        if isdir(file_path):
            raise FileNotFoundError('Unable to find a filename')

        func_result = x[1](basename(file_path))
        value = x[2].findall(func_result)[0]
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')
    except SyntaxError:
        raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')
    except (re.error, IndexError):
        raise re.error(f'Wrong regex pattern on {x[0]} annotation')

    return AnnotationTypes.FILENAME.name, value if value is not None else float('nan'), str


def _dirname_process(x: DirnameBuilder, original_header: List = [] or None, file_path: str = None,
                     annotation: dict = None) \
        -> DirnameProcess:
    """Get a Dirname value
    It will return a DirnameProcess describing the value to get from dirname annotation.
    Parameters
    ----------
    x : DirnameBuilder
        Annotation builder
    file_path: str
        Path of input file
    Returns
    -------
    str
        Annotation type
    float or int or str
        Fixed value
    Callable
        Function to execute on the fixed value
    """
    try:
        if isdir(file_path):
            raise FileNotFoundError('Unable to find a dirname')

        func_result = x[1](basename(dirname(abspath(file_path))))
        value = x[2].findall(func_result)[0]
    except TypeError:
        raise TypeError(f'Unable to parser {x[0]} annotation')
    except SyntaxError:
        raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')
    except (re.error, IndexError):
        raise re.error(f'Wrong regex pattern on {x[0]} annotation')

    return AnnotationTypes.DIRNAME.name, value if value is not None else float('nan'), str


def _mapping_process(x: MappingBuilder, original_header: List = [] or None, file_path: str = None,
                     header_schema: dict = None) \
        -> MappingProcess:
    """Get a Mapping value
    It will return a PluginProcess describing the value to get from plugin annotation.
    Parameters
    ----------
    x : PluginBuilder
        Annotation builder
    Returns
    -------
    str
        Annotation type
    None
        A None value, this value will not be taken into account
    Callable
        Function to execute on the fixed value
    """

    """
    if x[1] is None:
        raise ValueError(f'Wrong source fields on {x[0]} annotation')
    value = None

    for source in x[1]:
        try:
            map_key = header_schema[source][1]
            value = x[2].get(map_key, None)
        except KeyError:
            pass

    if value is None:
        raise KeyError(f'Unable to map {x[1]} sources on mapping annotation')
    """
    return AnnotationTypes.MAPPING.name, x, str #value if value is not None else float('nan'), str


def _plugin_process(x: PluginBuilder, original_header: List = [] or None, file_path: str = None,
                    annotation: dict = None) \
        -> PluginProcess:
    """Get a Plugin value
    It will return a PluginProcess describing the value to get from plugin annotation.
    Parameters
    ----------
    x : PluginBuilder
        Annotation builder
    Returns
    -------
    str
        Annotation type
    None
        A None value, this value will not be taken into account
    Callable
        Function to execute on the fixed value
    """
    if x[1] is None or x[2] is None:
        raise ValueError(f'Wrong function on {x[0]} annotation')
    return AnnotationTypes.PLUGIN.name, x[2], x[1]


class AnnotationTypesProcess(Enum):
    """Enum to get the value of every annotation Builder"""

    """Parser for static builder"""
    STATIC = partial(_static_process)

    """Parser for internal builder"""
    INTERNAL = partial(_internal_process)

    """Parser for filename builder"""
    FILENAME = partial(_filename_process)

    """Parser for dirname builder"""
    DIRNAME = partial(_dirname_process)

    """Parser for mapping builder"""
    MAPPING = partial(_mapping_process)

    """Parser for plugin builder"""
    PLUGIN = partial(_plugin_process)
