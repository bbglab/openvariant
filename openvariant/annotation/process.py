import re
from enum import Enum
from functools import partial
from os.path import isdir, basename, abspath, dirname
from typing import Tuple, List, Callable, Optional

from openvariant.annotation.builder import StaticBuilder, InternalBuilder, FilenameBuilder, DirnameBuilder, \
    PluginBuilder, MappingBuilder
from openvariant.annotation.config_annotation import AnnotationTypes
from openvariant.plugins.context import Context

StaticProcess = Tuple[str, float or int or str, Callable]
InternalProcess = Tuple[str, Tuple[dict, str], str]
FilenameProcess = Tuple[str, float or int or str, Callable]
DirnameProcess = Tuple[str, float or int or str, Callable]
PluginProcess = Tuple[str, Context, Callable]
MappingProcess = Tuple[str, MappingBuilder, Callable]


class STATIC:
    def __call__(self, x: StaticBuilder, original_header: List = [] or None, file_path: str = None,
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


class INTERNAL:
    def __call__(self, x: InternalBuilder, original_header: List = [] or None, file_path: str = None,
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
        field_pos = {}
        try:
            header_dict = {field: num for num, field in list(enumerate(original_header))}
            for source in x[1]:
                if isinstance(source, List):
                    for s in source:
                        try:
                            field_pos.update({s: header_dict[s]})
                        except KeyError:
                            field_pos = {}
                            pass
                    if len(field_pos) == len(source):
                        break
                    else:
                        field_pos = {}
                else:
                    try:
                        field_pos = {source: header_dict[source]}
                        break
                    except KeyError:
                        pass

        except TypeError:
            raise TypeError(f'Unable to parser {x[0]} annotation')
        except SyntaxError:
            raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')

        return AnnotationTypes.INTERNAL.name, (field_pos, x[3]), x[2]



class FILENAME:
    def __call__(self,x: FilenameBuilder, original_header: List = [] or None, file_path: str = None,
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
                raise FileNotFoundError('Unable to find_files a filename')

            func_result = x[1](basename(file_path))
            value = x[2].findall(func_result)[0]
        except TypeError:
            raise TypeError(f'Unable to parser {x[0]} annotation')
        except SyntaxError:
            raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')
        except (re.error, IndexError):
            raise re.error(f'Wrong regex pattern on {x[0]} annotation')

        return AnnotationTypes.FILENAME.name, value if value is not None else float('nan'), str


class DIRNAME:
    def __call__(self, x: DirnameBuilder, original_header: List = [] or None, file_path: str = None,
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
                raise FileNotFoundError('Unable to find_files a dirname')

            func_result = x[1](basename(dirname(abspath(file_path))))
            value = x[2].findall(func_result)[0]
        except TypeError:
            raise TypeError(f'Unable to parser {x[0]} annotation')
        except SyntaxError:
            raise SyntaxError(f'Unable to parser function lambda on {x[0]} annotation')
        except (re.error, IndexError):
            raise re.error(f'Wrong regex pattern on {x[0]} annotation')

        return AnnotationTypes.DIRNAME.name, value if value is not None else float('nan'), str


class MAPPING:
    def __call__(self, x: MappingBuilder, original_header: List = [] or None, file_path: str = None,
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
        return AnnotationTypes.MAPPING.name, x, str


class PLUGIN:
    def __call__(self, x: PluginBuilder, original_header: List = [] or None, file_path: str = None,
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
