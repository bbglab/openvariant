"""
Builder
====================================
A core Enum to build a specified Tuple for each annotation.
"""
import csv
import inspect
import os
import re
import glob
import gzip
import importlib
import importlib.util
from enum import Enum
from functools import partial
from os.path import dirname
from typing import Tuple, Any, List, Callable

from openvariant.config.config_annotation import AnnotationKeys, AnnotationTypes
from openvariant.plugins.context import Context
from openvariant.plugins.plugin import Plugin


class Builder:
    """A representation of a function in annotation file"""
    func: str = None

    def __init__(self, func: str) -> None:
        """
        Inits Builder with function or lambda in str format.

        Parameters
        ---------
        func : str
            A string that represents a function or a lambda described on the annotation file.
        """
        self.func = func

    def __call__(self, x: Any) -> Any:
        return eval(self.func)(x)


StaticBuilder = Tuple[str, float or int or str]
InternalBuilder = Tuple[str, List, Builder, str or float]
DirnameBuilder = Tuple[str, Builder, re.Pattern]
FilenameBuilder = Tuple[str, Builder, re.Pattern]
PluginBuilder = Tuple[str, Callable, Context]
MappingBuilder = Tuple[str, List, dict]


def _get_function_and_regexp(x: dict) -> Tuple[Builder, re.Pattern]:
    """Get the function and regular expression of an annotation
    Parameters
    ----------
    x : dict
        Annotation
    Returns
    -------
    Builder
        Represents the function described on the annotation.
    re.Pattern
        Regular expression to parse the annotation.
    """
    func_apply = Builder("(lambda y: y)") if AnnotationKeys.FUNCTION.value not in x \
        else Builder(x[AnnotationKeys.FUNCTION.value])
    try:
        regex_apply = re.compile('(.*)') if AnnotationKeys.REGEX.value not in x or x[AnnotationKeys.REGEX.value] is None \
            else re.compile(x[AnnotationKeys.REGEX.value])
    except re.error as e:
        raise re.error(f'Wrong regex pattern: {e}')
    return func_apply, regex_apply


def _static_builder(x: dict, base_path: str = None) -> StaticBuilder:
    """Built StaticBuilder from an annotation based on a static annotation with a fixed value.
    Parameters
    ----------
    x : dict
        Annotation
    Returns
    -------
    str
        Annotation type
    float or int or str
        Value of the field
    """
    try:
        value = x[AnnotationKeys.VALUE.value]
    except KeyError:
        raise KeyError('Static annotation is wrong specified.')
    return AnnotationTypes.STATIC.name, value


def _internal_builder(x: dict, base_path: str = None) -> InternalBuilder:
    """Built InternalBuilder from an annotation based on an internal annotation from fields of input files.
    Parameters
    ----------
    x : dict
        Annotation
    Returns
    -------
    str
        Annotation type
    str
        Value of the field
    Builder
        Representation of the function to apply on the annotation value
    """
    try:
        value = x[AnnotationKeys.VALUE.value]
    except KeyError:
        value = float('nan')

    return AnnotationTypes.INTERNAL.name, x[AnnotationKeys.FIELD_SOURCE.value], Builder("(lambda y: y)") \
        if AnnotationKeys.FUNCTION.value not in x or x[AnnotationKeys.FUNCTION.value] is None or \
           len(x[AnnotationKeys.FUNCTION.value]) == 2 else Builder(x[AnnotationKeys.FUNCTION.value]), value


def _dirname_builder(x: dict, base_path: str = None) -> DirnameBuilder:
    """Built DirnameBuilder from an annotation based on a dirname annotation, getting the dirname which input files
    are located.
    Parameters
    ----------
    x : dict
        Annotation
    Returns
    -------
    str
        Annotation type
    Builder
        Representation of the function to apply on the annotation value (dirname).
    re.Pattern
        Representation of a regular expression to apply on the annotation value (dirname).
    """
    func_apply, regex_apply = _get_function_and_regexp(x)

    return AnnotationTypes.DIRNAME.name, func_apply, regex_apply


def _filename_builder(x: dict, base_path: str = None) -> FilenameBuilder:
    """Built FilenameBuilder from an annotation based on a filename annotation, getting the filename of each input file.
    Parameters
    ----------
    x : dict
        Annotation
    Returns
    -------
    str
        Annotation type
    Builder
        Representation of the function to apply on the annotation value (filename).
    re.Pattern
        Representation of a regular expression to apply on the annotation value (filename).
    """
    func_apply, regex_apply = _get_function_and_regexp(x)

    return AnnotationTypes.FILENAME.name, func_apply, regex_apply


def _get_plugin_function(mod) -> Callable:
    """Get the function from the module
    Parameters
    ----------
    mod
        Plugin module where 'run' function is imported
    Returns
    -------
    Callable
        'run' function to execute data transformation
    """
    func = None
    cls_members = inspect.getmembers(mod, inspect.isclass)
    for (_, c) in cls_members:
        if issubclass(c, Plugin) & (c is not Plugin):
            func = c().run
            break
    return func


def _get_plugin_context(mod) -> Any:
    ctxt = None
    cls_members = inspect.getmembers(mod, inspect.isclass)
    for (_, c) in cls_members:
        if issubclass(c, Context) & (c is not Context):
            ctxt = c
            break
    return ctxt


def _mapping_builder(x: dict, base_path: str) -> MappingBuilder:
    """Built MappingBuilder from an annotation based on a mapping annotation, it matches the value of the input file to
    a value that appears in the mapping file. It will return the value of one field of the mapping that has been
    indicated on the annotation.
    Parameters
    ----------
    x : dict
        Annotation.
    base_path : str
        A base path where file that is parsing is located.
    Returns
    -------
    str
        Annotation type.
    List
        Fields that has to look for in the input files.
    dict
        Schema of the mapping file, where 'key' is the value of one column (fieldMapping) in mapping file and
        'value' is the value of one column (valueMapping) in the mapping file
    """
    values: dict = {}
    mapping_files = x[AnnotationKeys.FILE_MAPPING.value]
    files = list(glob.iglob(f"{dirname(base_path)}/{mapping_files}", recursive=True))
    if len(files) == 0:
        raise FileNotFoundError(f"Unable to find '{mapping_files}' file in '{dirname(base_path)}'")
    try:
        for mapping_file in files:
            open_method = gzip.open if mapping_file.endswith('gz') else open
            with open_method(mapping_file, "rt") as fd:
                for r in csv.DictReader(fd, delimiter='\t'):
                    field = r[x[AnnotationKeys.FIELD_MAPPING.value]]
                    val = r[x[AnnotationKeys.FIELD_VALUE.value]]
                    values[field] = val
            break
    except TypeError:
        raise TypeError("Unable to parse mapping annotation")
    return AnnotationTypes.MAPPING.name, x[AnnotationKeys.FIELD_SOURCE.value], values


def _plugin_builder(x: dict, base_path: str = None) -> PluginBuilder:
    """Built PluginBuilder from an annotation based on a plugin annotation, from an internal or a customized plugin
    which data is transformed and executed thought a process.
    Parameters
    ----------
    x : dict
        Annotation
    Returns
    -------
    str
        Annotation type
    Builder
        Representation of the function to apply on the annotation value (plugin's 'run' function).
    """
    func = None
    ctxt = None
    try:
        mod = importlib.import_module(f".{x[AnnotationTypes.PLUGIN.value]}", package="openvariant.plugins")
        func = _get_plugin_function(mod)
        ctxt = _get_plugin_context(mod)
    except ModuleNotFoundError:
        try:
            files = list(glob.iglob(f"{os.getcwd()}/**/{x[AnnotationTypes.PLUGIN.value]}", recursive=True))
            if len(files) == 0:
                raise FileNotFoundError(f"Unable to find '{x[AnnotationTypes.PLUGIN.value]}' plugin in '{os.getcwd()}'")
            else:
                try:
                    for package in files:
                        spec = importlib.util.spec_from_file_location(f".{x[AnnotationTypes.PLUGIN.value]}",
                                                                      f"{package}/{x[AnnotationTypes.PLUGIN.value]}.py")
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)

                        func = _get_plugin_function(mod)
                        ctxt = _get_plugin_context(mod)
                except (ImportError, AttributeError):
                    raise ImportError(f"Unable to import 'run' on the plugin.")
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f"Unable to found '{x[AnnotationTypes.PLUGIN.value]}' plugin.")
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Unable to import the plugin: {e}")

    return AnnotationTypes.PLUGIN.name, func, ctxt


class AnnotationTypesBuilders(Enum):
    """Enum to construct every annotation type builder"""

    """Builder for static annotation"""
    STATIC = partial(_static_builder)

    """Builder for internal annotation"""
    INTERNAL = partial(_internal_builder)

    """Builder for dirname annotation"""
    DIRNAME = partial(_dirname_builder)

    """Builder for filename annotation"""
    FILENAME = partial(_filename_builder)

    """Builder for mapping annotation"""
    MAPPING = partial(_mapping_builder)

    """Builder for plugin annotation"""
    PLUGIN = partial(_plugin_builder)
