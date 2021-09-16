import importlib
from enum import Enum
from functools import partial
from typing import List, Tuple, Callable, Any

from src.config.config_annotation import AnnotationTypes, AnnotationKeys


def _static_builder(x: dict) -> Tuple[str, Any]:
    return AnnotationTypes.STATIC.name, x[AnnotationKeys.VALUE.value]


def _internal_builder(x: dict) -> Tuple[str, List]:
    return AnnotationTypes.INTERNAL.name, x[AnnotationKeys.FIELD_SOURCE.value]


def _dirname_builder(x: dict) -> Tuple[str, Callable]:
    return AnnotationTypes.DIRNAME.name, (lambda y: y) \
        if x[AnnotationKeys.FUNCTION.value] is None or len(x[AnnotationKeys.FUNCTION.value]) == 2 \
        else eval(x[AnnotationKeys.FUNCTION.value])


def _filename_builder(x: dict) -> Tuple[str, Callable]:
    return AnnotationTypes.FILENAME.name, \
           (lambda y: y) if x[AnnotationKeys.FUNCTION.value] is None or len(x[AnnotationKeys.FUNCTION.value]) == 2 \
               else eval(x[AnnotationKeys.FUNCTION.value])


def _plugin_builder(x: dict) -> Tuple[str, List, Callable]:
    try:
        mod = importlib.import_module(f".{x[AnnotationTypes.PLUGIN.value]}", package="plugins")
        func = getattr(mod, x[AnnotationTypes.PLUGIN.value])
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Enable to found 'plugins.{x[AnnotationTypes.PLUGIN.value]}' module.")
    return AnnotationTypes.PLUGIN.name, x[AnnotationKeys.FIELD_SOURCE.value], func


'''
def _liftover_builder(x: dict) -> Tuple[str, str, str, str]:
    return AnnotationTypes.LIFTOVER.name, x[AnnotationKeys.COORDINATE_SOURCE.value], \
           x[AnnotationKeys.COORDINATE_TARGET.value], x[AnnotationKeys.FIELD_SOURCE.value]


def _mapping_builder(x: dict) -> Tuple[str, List]:
    values: List = []
    with open(x[AnnotationKeys.MAPPING_FILE.value]) as f:
        for r in csv.DictReader(f, delimiter='\t'):
            val = r[x[AnnotationKeys.MAPPING_FIELD.value]]
            values.append(val)
    return AnnotationTypes.MAPPING.name, values
'''


class AnnotationTypesBuilders(Enum):
    STATIC = partial(_static_builder)
    INTERNAL = partial(_internal_builder)
    DIRNAME = partial(_dirname_builder)
    FILENAME = partial(_filename_builder)
    PLUGIN = partial(_plugin_builder)
    # MAPPING = partial(_mapping_builder)
