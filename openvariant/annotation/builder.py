import csv
import re
import glob
import gzip
import importlib
from enum import Enum
from functools import partial
from typing import List, Tuple, Callable, Any

from openvariant.config.config_annotation import AnnotationTypes, AnnotationKeys


class Builder:
    func: str = None

    def __init__(self, func: str) -> None:
        self.func = func

    def __call__(self, x: Any) -> Any:
        return eval(self.func)(x)


def _static_builder(x: dict) -> Tuple[str, Any]:
    return AnnotationTypes.STATIC.name, x[AnnotationKeys.VALUE.value]


def _internal_builder(x: dict) -> Tuple[str, List, Builder, str]:
    try:
        value = x[AnnotationKeys.VALUE.value]
    except KeyError:
        value = float('nan')

    return AnnotationTypes.INTERNAL.name, x[AnnotationKeys.FIELD_SOURCE.value], Builder("(lambda y: y)") \
        if AnnotationKeys.FUNCTION.value not in x or len(x[AnnotationKeys.FUNCTION.value]) == 2 \
        else Builder(x[AnnotationKeys.FUNCTION.value]), value


def _get_dirname_filename_attributes(x: dict) -> Tuple[Builder, re.Pattern]:
    func_apply = Builder("(lambda y: y)") if AnnotationKeys.FUNCTION.value not in x \
        else Builder(x[AnnotationKeys.FUNCTION.value])
    regex_apply = re.compile('(.*)') if AnnotationKeys.REGEX.value not in x \
        else re.compile(x[AnnotationKeys.REGEX.value])
    return func_apply, regex_apply


def _dirname_builder(x: dict) -> Tuple[str, Builder, re.Pattern]:
    func_apply, regex_apply = _get_dirname_filename_attributes(x)

    return AnnotationTypes.DIRNAME.name, func_apply, regex_apply


def _filename_builder(x: dict) -> Tuple[str, Builder, re.Pattern]:
    func_apply, regex_apply = _get_dirname_filename_attributes(x)

    return AnnotationTypes.FILENAME.name, func_apply, regex_apply


def _plugin_builder(x: dict) -> Tuple[str, List, Callable]:
    try:
        mod = importlib.import_module(f".{x[AnnotationTypes.PLUGIN.value]}", package="plugins")
        func = getattr(mod, x[AnnotationTypes.PLUGIN.value])
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Enable to found 'plugins.{x[AnnotationTypes.PLUGIN.value]}' module.")
    return AnnotationTypes.PLUGIN.name, x[AnnotationKeys.FIELD_SOURCE.value], func


def _mapping_builder(x: dict) -> Tuple[str, List, dict]:
    values: dict = {}
    mapping_files = x[AnnotationKeys.FILE_MAPPING.value]
    for mapping_file in glob.glob('**/' + mapping_files, recursive=True)[:1]:
        open_method = gzip.open if mapping_file.endswith('gz') else open
        with open_method(mapping_file, "rt") as fd:
            for r in csv.DictReader(fd, delimiter='\t'):
                field = r[x[AnnotationKeys.FIELD_MAPPING.value]]
                val = r[x[AnnotationKeys.FIELD_VALUE.value]]
                values[field] = val
    return AnnotationTypes.MAPPING.name, x[AnnotationKeys.FIELD_SOURCE.value], values


class AnnotationTypesBuilders(Enum):
    STATIC = partial(_static_builder)
    INTERNAL = partial(_internal_builder)
    DIRNAME = partial(_dirname_builder)
    FILENAME = partial(_filename_builder)
    PLUGIN = partial(_plugin_builder)
    MAPPING = partial(_mapping_builder)
