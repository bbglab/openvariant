import logging
import re
from os.path import basename

from typing import List
from yaml import safe_load, YAMLError

from src.annotation.builder import AnnotationTypesBuilders
from src.config.config_annotation import (AnnotationGeneralKeys,
                                          AnnotationKeys,
                                          AnnotationTypes,
                                          ExcludesKeys,
                                          DEFAULT_FORMAT)


def _read_annotation_file(path: str) -> dict:
    with open(path, 'r') as stream:
        try:
            return safe_load(stream)
        except YAMLError as exc:
            logging.error(exc)


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

    # Excludes key
    if AnnotationGeneralKeys.EXCLUDES.value in annot and \
            (not all(ExcludesKeys.FIELD.value in x and ExcludesKeys.VALUE.value in x
                     for x in annot[AnnotationGeneralKeys.EXCLUDES.value]) or not all(
                isinstance(x[ExcludesKeys.FIELD.value], str) for x in annot[AnnotationGeneralKeys.EXCLUDES.value])):
        raise KeyError(f"'{AnnotationGeneralKeys.EXCLUDES.value}' key in bad format.")


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
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.LIFTOVER.value) and \
            AnnotationKeys.FIELD_SOURCE.value in annot and \
            not all(isinstance(x, str) for x in annot[AnnotationKeys.FIELD_SOURCE.value]):
        raise KeyError(f"'{AnnotationKeys.FIELD_SOURCE.value}' key not found or is not a list of str.")

    # Dirname and filename key
    if (annot[AnnotationKeys.TYPE.value] == AnnotationTypes.DIRNAME.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.FILENAME.value) and \
            AnnotationKeys.FUNCTION.value in annot and \
            re.compile("lambda[' ']+[a-zA-Z0-9]+[' ']*:[' ']*.*").search(annot[AnnotationKeys.FUNCTION.value]) is None:
        raise ValueError(f"'{AnnotationKeys.FUNCTION.value}' value is not an appropriated lambda function.")

    # Coordinate key
    if annot[AnnotationKeys.TYPE.value] == AnnotationTypes.LIFTOVER.value and \
            ((
                     AnnotationKeys.COORDINATE_SOURCE.value not in annot and AnnotationKeys.COORDINATE_TARGET.value not in annot) or
             (not isinstance(annot[AnnotationKeys.COORDINATE_SOURCE.value], str) and
              not isinstance(annot[AnnotationKeys.COORDINATE_TARGET.value], str))):
        raise KeyError(f"'{AnnotationKeys.COORDINATE.value}' key not found or is not a str.")

    # Mapping keys
    if annot[AnnotationKeys.TYPE.value] == AnnotationTypes.MAPPING.value and \
            (AnnotationKeys.MAPPING_FILE.value not in annot or
             AnnotationKeys.MAPPING_FIELD.value not in annot or
             not isinstance(annot[AnnotationKeys.MAPPING_FILE.value], str) or
             not isinstance(annot[AnnotationKeys.MAPPING_FIELD.value], str)):
        raise KeyError(
            f"'{AnnotationKeys.MAPPING_FIELD.value}' or '{AnnotationKeys.MAPPING_FILE.value}' key not found or are not "
            f"a str.")


class Annotation:
    _builders: dict = {}

    def __init__(self, path: str) -> None:
        self._builders: dict = {}
        self._annotations: dict = {}
        self._structure: dict = {}

        self._register_builders()
        self._path = path
        self._raw_annotation = _read_annotation_file(path)

        self._patterns = self._raw_annotation[AnnotationGeneralKeys.PATTERN.value]
        self._recursive = self._raw_annotation.get(AnnotationGeneralKeys.RECURSIVE.value, True)
        self._excludes = self._raw_annotation.get(AnnotationGeneralKeys.EXCLUDES.value, [])
        self._format = self._raw_annotation.get(AnnotationGeneralKeys.FORMAT.value, DEFAULT_FORMAT).replace('.', '')

        self.check_annotation()
        self.extract_annotation()

    def _register_builders(self) -> None:
        for b in AnnotationTypes:
            self._builders[b.value] = AnnotationTypesBuilders[b.name].value

    def check_annotation(self) -> bool:
        try:
            _check_general_keys(self._raw_annotation)
            if AnnotationGeneralKeys.ANNOTATION.value in self._raw_annotation:
                for annot in self._raw_annotation[AnnotationGeneralKeys.ANNOTATION.value]:
                    _check_annotation_keys(annot)
            return True
        except Exception as e:
            logging.error(e)

    def extract_annotation(self) -> None:
        for k in self._raw_annotation.get(AnnotationGeneralKeys.ANNOTATION.value, []):
            self._annotations[k[AnnotationKeys.FIELD.value]] = \
                AnnotationTypesBuilders[k[AnnotationKeys.TYPE.value].upper()].value(k)

        structure_aux = self._annotations
        structure_aux[AnnotationGeneralKeys.EXCLUDES.name] = self._excludes
        self._structure = {e: structure_aux for e in self._patterns}

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
    def annotations(self) -> dict:
        return self._annotations

    @property
    def excludes(self) -> dict:
        return self._excludes

    @property
    def structure(self) -> dict:
        return self._structure


def merge_annotations_structure(ann_a: dict, ann_b: dict) -> dict:
    """
    :param ann_a: The first annotations structure
    :param ann_b: The second annotations structure. This annotations
    have preference and will override A annotations if there is a conflict
    :return: The merge of A and B annotation structure
    """

    # Clone A
    aa = {k: dict(v) for k, v in ann_a.items()}

    # Update or add B entries
    for k, v in ann_b.items():
        if k in aa:
            # Update the annotations
            for kv, vv in v.items():
                if kv not in aa[k]:
                    aa[k][kv] = vv
                else:
                    if isinstance(aa[k][kv], list):
                        # If it's a list concat them instead of override it
                        if len(vv) > 0:
                            vv_list = vv if isinstance(vv, list) else [vv]
                            aa[k][kv] = list(aa[k][kv]) + vv_list
                    else:
                        # Override the value
                        if vv != {}:
                            aa[k][kv] = vv
        else:
            aa[k] = {k: v for k, v in aa['global'].items()} if 'global' in aa else {}
            aa[k].update(v)

    return aa


def process_annotations(annotations, base_path, filename):
    # Annotate filename base annotations
    for k in annotations:
        value = annotations[k]
        if isinstance(value, tuple):
            if value[0] in [AnnotationTypes.FILENAME.name, AnnotationTypes.DIRNAME.name]:
                name = filename if value[0] == AnnotationTypes.FILENAME.name else basename(base_path)
                annotations[k] = value[1](name)

    # Try to annotate mappings that only use already resolved annotations
    '''
    for k in annotations:
        value = annotations[k]
        if isinstance(value, tuple):
            if value[0] == 'mapping':
                print(value)
                map_key = annotations[value[1]]
                if not isinstance(map_key, tuple):
                    annotations[k] = value[2].get(map_key, None)
    '''

    return annotations
