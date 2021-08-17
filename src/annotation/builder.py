import csv
from enum import Enum
from functools import partial
from typing import List, Tuple, Callable, Any

from src.config.config_annotation import AnnotationTypes, AnnotationKeys


def static_builder(x: dict) -> Tuple[str, Any]:
    return AnnotationTypes.STATIC.name, x[AnnotationKeys.VALUE.value]


def internal_builder(x: dict) -> Tuple[str, List]:
    return AnnotationTypes.INTERNAL.name, x[AnnotationKeys.FIELD_SOURCE.value]


def dirname_builder(x: dict) -> Tuple[str, Callable]:
    return AnnotationTypes.DIRNAME.name, (lambda y: y) \
        if x[AnnotationKeys.FUNCTION.value] is None or len(x[AnnotationKeys.FUNCTION.value]) == 2 \
        else eval(x[AnnotationKeys.FUNCTION.value])


def filename_builder(x: dict) -> Tuple[str, Callable]:
    return AnnotationTypes.FILENAME.name, \
           (lambda y: y) if x[AnnotationKeys.FUNCTION.value] is None or len(x[AnnotationKeys.FUNCTION.value]) == 2 \
           else eval(x[AnnotationKeys.FUNCTION.value])


def liftover_builder(x: dict) -> Tuple[str, str, str, str]:
    return AnnotationTypes.LIFTOVER.value, x[AnnotationKeys.COORDINATE_SOURCE.value], \
           x[AnnotationKeys.COORDINATE_TARGET.value], x[AnnotationKeys.FIELD_SOURCE.value]


def mapping_builder(x: dict) -> Tuple[str, List]:
    values: List = []
    with open(x[AnnotationKeys.MAPPING_FILE.value]) as f:
        for r in csv.DictReader(f, delimiter='\t'):
            val = r[x[AnnotationKeys.MAPPING_FIELD.value]]
            values.append(val)
    return AnnotationTypes.MAPPING.value, values


class AnnotationTypesBuilders(Enum):
    STATIC = partial(static_builder)
    INTERNAL = partial(internal_builder)
    DIRNAME = partial(dirname_builder)
    FILENAME = partial(filename_builder)
    LIFTOVER = partial(liftover_builder)
    MAPPING = partial(mapping_builder)
