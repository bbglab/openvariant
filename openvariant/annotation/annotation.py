import copy
import logging
import re

from typing import List
from yaml import safe_load, YAMLError

from openvariant.annotation.builder import AnnotationTypesBuilders
from openvariant.config.config_annotation import (AnnotationGeneralKeys,
                                                  AnnotationKeys,
                                                  AnnotationTypes,
                                                  ExcludesKeys,
                                                  DEFAULT_FORMAT, DEFAULT_DELIMITER)


def _read_annotation_file(path: str) -> dict:
    with open(path, 'r') as stream:
        try:
            return safe_load(stream)
        except YAMLError as exc:
            logging.error(exc)
        stream.close()


def _check_general_keys(annot: dict) -> None:
    # Pattern key
    if AnnotationGeneralKeys.PATTERN.value not in annot or not isinstance(
            annot[AnnotationGeneralKeys.PATTERN.value], list) \
            and not all(isinstance(x, str) for x in annot[AnnotationGeneralKeys.PATTERN.value]):
        raise KeyError(f"'{AnnotationGeneralKeys.PATTERN.value}' key not found or is not a str.")

    # Recursive key
    if AnnotationGeneralKeys.RECURSIVE.value in annot and \
            not isinstance(annot[AnnotationGeneralKeys.RECURSIVE.value], bool):
        raise KeyError(f"'{AnnotationGeneralKeys.RECURSIVE.value}' key is not a boolean.")

    # Format key
    if AnnotationGeneralKeys.FORMAT.value in annot and not isinstance(
            annot[AnnotationGeneralKeys.FORMAT.value], str):
        raise KeyError(f"'{AnnotationGeneralKeys.FORMAT.value}' key is not a string.")

    # Delimiter key
    if AnnotationGeneralKeys.DELIMITER.value in annot and not isinstance(
            annot[AnnotationGeneralKeys.DELIMITER.value], str):
        raise KeyError(f"'{AnnotationGeneralKeys.DELIMITER.value}' key is not a string.")

    # Annotations key
    if AnnotationGeneralKeys.ANNOTATION.value in annot and not isinstance(annot[AnnotationGeneralKeys.ANNOTATION.value],
                                                                          list):
        raise KeyError(f"'{AnnotationGeneralKeys.ANNOTATION.value}' key is not a list.")

    # Excludes key
    if AnnotationGeneralKeys.EXCLUDE.value in annot and \
            (not all(ExcludesKeys.FIELD.value in x and ExcludesKeys.VALUE.value in x
                     for x in annot[AnnotationGeneralKeys.EXCLUDE.value]) or not all(
                isinstance(x[ExcludesKeys.FIELD.value], str) for x in annot[AnnotationGeneralKeys.EXCLUDE.value])):
        raise KeyError(f"'{AnnotationGeneralKeys.EXCLUDE.value}' key in bad format.")


def _check_annotation_keys(annot: dict) -> None:
    # Type key
    if AnnotationKeys.TYPE.value not in annot or not isinstance(annot[AnnotationKeys.TYPE.value], str):
        raise KeyError(f"'{AnnotationKeys.TYPE.value}' key not found or is not a str.")
    if annot[AnnotationKeys.TYPE.value] not in [e.value for e in AnnotationTypes]:
        raise ValueError(f"'{AnnotationKeys.TYPE.value}' value is wrong.")

    # Field key
    if AnnotationKeys.FIELD.value not in annot or not isinstance(annot[AnnotationKeys.FIELD.value], str):
        raise KeyError(f"'{AnnotationKeys.FIELD.value}' key not found or is not a str.")

    # Field source key
    if (annot[AnnotationKeys.TYPE.value] == AnnotationTypes.INTERNAL.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.PLUGIN.value) and \
            AnnotationKeys.FIELD_SOURCE.value in annot and \
            not all(isinstance(x, str) for x in annot[AnnotationKeys.FIELD_SOURCE.value]):
        raise KeyError(f"'{AnnotationKeys.FIELD_SOURCE.value}' key not found or is not a list of str.")

    # Dirname and filename key
    if (annot[AnnotationKeys.TYPE.value] == AnnotationTypes.DIRNAME.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.FILENAME.value) and \
            AnnotationKeys.FUNCTION.value in annot and \
            re.compile("lambda[' ']+[a-zA-Z0-9]+[' ']*:[' ']*.*").search(annot[AnnotationKeys.FUNCTION.value]) is None:
        raise ValueError(f"'{AnnotationKeys.FUNCTION.value}' value is not an appropriated lambda function.")

    # Plugin key
    if annot[AnnotationKeys.TYPE.value] == AnnotationTypes.PLUGIN.value and \
            AnnotationKeys.PLUGIN.value not in annot:
        raise KeyError(f"'{AnnotationKeys.PLUGIN.value}' key not found.")

    if annot[AnnotationKeys.TYPE.value] == AnnotationTypes.PLUGIN.value and \
            (AnnotationKeys.PLUGIN.value in annot and not isinstance(annot[AnnotationKeys.PLUGIN.value], str)):
        raise ValueError(f"'{AnnotationKeys.PLUGIN.value}' is not a str.")

    # Mapping keys
    # if annot[AnnotationKeys.TYPE.value] == AnnotationTypes.MAPPING.value and \
    #        (AnnotationKeys.MAPPING_FILE.value not in annot or
    #         AnnotationKeys.MAPPING_FIELD.value not in annot or
    #         not isinstance(annot[AnnotationKeys.MAPPING_FILE.value], str) or
    #         not isinstance(annot[AnnotationKeys.MAPPING_FIELD.value], str)):
    #    raise KeyError(
    #        f"'{AnnotationKeys.MAPPING_FIELD.value}' or '{AnnotationKeys.MAPPING_FILE.value}' key not found or are not "
    #        f"a str.")


class Annotation:
    _builders: dict = {}

    def __init__(self, path: str) -> None:
        self._builders: dict = {}

        self._register_builders()
        self._path = path
        raw_annotation = _read_annotation_file(path)
        _check_general_keys(raw_annotation)
        for annot in raw_annotation.get(AnnotationGeneralKeys.ANNOTATION.value, []):
            _check_annotation_keys(annot)

        self._patterns = raw_annotation[AnnotationGeneralKeys.PATTERN.value]
        self._recursive = raw_annotation.get(AnnotationGeneralKeys.RECURSIVE.value, True)
        self._delimiter = raw_annotation.get(AnnotationGeneralKeys.DELIMITER.value, DEFAULT_DELIMITER).upper()
        self._excludes = raw_annotation.get(AnnotationGeneralKeys.EXCLUDE.value, [])
        self._format = raw_annotation.get(AnnotationGeneralKeys.FORMAT.value, DEFAULT_FORMAT).replace('.', '')

        self._annotations: dict = {}
        for k in raw_annotation.get(AnnotationGeneralKeys.ANNOTATION.value, []):
            self._annotations[k[AnnotationKeys.FIELD.value]] = \
                AnnotationTypesBuilders[k[AnnotationKeys.TYPE.value].upper()].value(k)

    def _register_builders(self) -> None:
        for b in AnnotationTypes:
            self._builders[b.value] = AnnotationTypesBuilders[b.name].value

    #def transform_dirname_filename(self, base_path: str):
    #    for ka in self._annotations:
    #        name = None
    #        if self._annotations[ka][0] == AnnotationTypes.FILENAME.name:
    #            name = basename(base_path)
    #        elif self._annotations[ka][0] == AnnotationTypes.DIRNAME.name:
    #            if isfile(base_path):
    #                name = basename(dirname(base_path))
    #            else:
    #                name = basename(base_path)
    #        if (self._annotations[ka][0] == AnnotationTypes.FILENAME.name or
    #            self._annotations[ka][0] == AnnotationTypes.DIRNAME.name) \
    #                and callable(self._annotations[ka][1]):
    #            self._annotations[ka] = (self._annotations[ka][0], self._annotations[ka][1](name))

    def set_patterns(self, patterns: List[str]) -> None:
        self._patterns = patterns

    def set_excludes(self, excludes: List) -> None:
        self._excludes = excludes

    def set_annotations(self, annotations) -> None:
        self._annotations = annotations

    @property
    def recursive(self) -> bool:
        return self._recursive

    @property
    def patterns(self) -> List[str]:
        return self._patterns

    @property
    def format(self) -> str:
        return self._format

    @property
    def delimiter(self) -> str:
        return self._delimiter

    @property
    def annotations(self) -> dict:
        return self._annotations

    @property
    def excludes(self) -> List:
        return self._excludes

    @property
    def structure(self) -> dict:

        structure_aux = {AnnotationGeneralKeys.ANNOTATION.name: self._annotations,
                         AnnotationGeneralKeys.EXCLUDE.name: self._excludes}
        return {e: structure_aux for e in self._patterns}


def merge_annotations_structure(ann_a: Annotation, ann_b: Annotation) -> Annotation:
    """
    :param ann_a: The first Annotation. This annotation
    has preference and will override B annotation if there is a conflict
    :param ann_b: The second Annotation.
    :return: The merge of A and B annotation
    """
    if ann_a is None:
        return copy.deepcopy(ann_b)
    elif ann_b is None:
        return copy.deepcopy(ann_a)

    ann_aa = copy.deepcopy(ann_a)

    ann_aa.set_patterns(list(set(ann_aa.patterns).union(set(ann_b.patterns))))

    excludes_total = ann_aa.excludes

    for k in ann_b.excludes:
        if k not in excludes_total:
            excludes_total.append(k)

    ann_aa.set_excludes(excludes_total)

    aa = {k: v for k, v in ann_aa.annotations.items()}
    for k, v in ann_b.annotations.items():
        if k not in list(aa.keys()):
            aa[k] = v

    ann_aa.set_annotations(aa)
    return ann_aa