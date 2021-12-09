import csv
import re
import glob
import gzip
import importlib
from enum import Enum
from functools import partial
from os.path import dirname
from typing import Tuple, Any, List, Callable

from openvariant.config.config_annotation import AnnotationKeys, AnnotationTypes


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


def _plugin_builder(x: dict, base_path: str = None) -> PluginBuilder:
    try:
        mod = importlib.import_module(f".{x[AnnotationTypes.PLUGIN.value]}", package="plugins")
        func = getattr(mod, x[AnnotationTypes.PLUGIN.value])
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Unable to found '{x[AnnotationTypes.PLUGIN.value]}' plugin.")
    field_sources = x[AnnotationKeys.FIELD_SOURCE.value] if AnnotationKeys.FIELD_SOURCE.value in x else []
    return AnnotationTypes.PLUGIN.name, field_sources, func


def _mapping_builder(x: dict, path: str) -> MappingBuilder:
    values: dict = {}
    mapping_files = x[AnnotationKeys.FILE_MAPPING.value]
    files = list(glob.iglob(dirname(path) + '/**/' + mapping_files, recursive=True))
    if len(files) == 0:
        raise FileNotFoundError(f'Unable to find \'{mapping_files}\' file')
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
