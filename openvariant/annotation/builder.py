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
from openvariant.plugins.plugin import Plugin


class Builder:
    func: str = None

    def __init__(self, func: str) -> None:
        self.func = func

    def __call__(self, x: Any) -> Any:
        return eval(self.func)(x)


StaticBuilder = Tuple[str, float or int or str]
InternalBuilder = Tuple[str, List, Builder, str or float]
DirnameBuilder = Tuple[str, Builder, re.Pattern]
FilenameBuilder = Tuple[str, Builder, re.Pattern]
PluginBuilder = Tuple[str, List, Callable]
MappingBuilder = Tuple[str, List, dict]


def _get_dirname_filename_attributes(x: dict) -> Tuple[Builder, re.Pattern]:
    func_apply = Builder("(lambda y: y)") if AnnotationKeys.FUNCTION.value not in x \
        else Builder(x[AnnotationKeys.FUNCTION.value])
    try:
        regex_apply = re.compile('(.*)') if AnnotationKeys.REGEX.value not in x or x[AnnotationKeys.REGEX.value] is None \
            else re.compile(x[AnnotationKeys.REGEX.value])
    except re.error as e:
        raise re.error(f'Wrong regex pattern: {e}')
    return func_apply, regex_apply


def _static_builder(x: dict, base_path: str = None) -> StaticBuilder:
    try:
        value = x[AnnotationKeys.VALUE.value]
    except KeyError:
        raise KeyError('Static annotation is wrong specified.')
    return AnnotationTypes.STATIC.name, value


def _internal_builder(x: dict, base_path: str = None) -> InternalBuilder:
    try:
        value = x[AnnotationKeys.VALUE.value]
    except KeyError:
        value = float('nan')

    return AnnotationTypes.INTERNAL.name, x[AnnotationKeys.FIELD_SOURCE.value], Builder("(lambda y: y)") \
        if AnnotationKeys.FUNCTION.value not in x or x[AnnotationKeys.FUNCTION.value] is None or \
           len(x[AnnotationKeys.FUNCTION.value]) == 2 else Builder(x[AnnotationKeys.FUNCTION.value]), value


def _dirname_builder(x: dict, base_path: str = None) -> DirnameBuilder:
    func_apply, regex_apply = _get_dirname_filename_attributes(x)

    return AnnotationTypes.DIRNAME.name, func_apply, regex_apply


def _filename_builder(x: dict, base_path: str = None) -> FilenameBuilder:
    func_apply, regex_apply = _get_dirname_filename_attributes(x)

    return AnnotationTypes.FILENAME.name, func_apply, regex_apply


def _get_plugin_function(mod) -> Callable:
    func = None
    cls_members = inspect.getmembers(mod, inspect.isclass)
    for (_, c) in cls_members:
        if issubclass(c, Plugin) & (c is not Plugin):
            func = c().run
            break
    return func


def _plugin_builder(x: dict, base_path: str = None) -> PluginBuilder:
    func = None
    try:
        mod = importlib.import_module(f".{x[AnnotationTypes.PLUGIN.value]}", package="plugins")
        func = _get_plugin_function(mod)
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
                except (ImportError, AttributeError):
                    raise ImportError(f"Unable to import 'run' on the plugin.")
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f"Unable to found '{x[AnnotationTypes.PLUGIN.value]}' plugin.")
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Unable to import the plugin: {e}")

    field_sources = x[AnnotationKeys.FIELD_SOURCE.value] if AnnotationKeys.FIELD_SOURCE.value in x else []
    return AnnotationTypes.PLUGIN.name, field_sources, func


def _mapping_builder(x: dict, path: str) -> MappingBuilder:
    values: dict = {}
    mapping_files = x[AnnotationKeys.FILE_MAPPING.value]
    files = list(glob.iglob(f"{dirname(path)}/**/{mapping_files}", recursive=True))
    if len(files) == 0:
        raise FileNotFoundError(f"Unable to find '{mapping_files}' file in '{dirname(path)}'")
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


class AnnotationTypesBuilders(Enum):
    STATIC = partial(_static_builder)
    INTERNAL = partial(_internal_builder)
    DIRNAME = partial(_dirname_builder)
    FILENAME = partial(_filename_builder)
    PLUGIN = partial(_plugin_builder)
    MAPPING = partial(_mapping_builder)
