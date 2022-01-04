"""
Annotation
====================================
A core class to represent the schema which files will be parsed.
"""
import logging
import re

from typing import List
from yaml import safe_load, YAMLError

from openvariant.annotation.builder import AnnotationTypesBuilders
from openvariant.config.config_annotation import (AnnotationGeneralKeys, AnnotationKeys, AnnotationTypes,
                                                  ExcludesKeys, DEFAULT_FORMAT, DEFAULT_DELIMITER,
                                                  DEFAULT_COLUMNS, AnnotationFormat, AnnotationDelimiter)


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
    if AnnotationGeneralKeys.FORMAT.value in annot and \
            (not isinstance(annot[AnnotationGeneralKeys.FORMAT.value], str) or
             annot[AnnotationGeneralKeys.FORMAT.value].upper() not in [e.name for e in AnnotationFormat]):
        raise KeyError(f"'{AnnotationGeneralKeys.FORMAT.value}' key is not a string.")

    # Delimiter key
    if AnnotationGeneralKeys.DELIMITER.value in annot and \
            (not isinstance(annot[AnnotationGeneralKeys.DELIMITER.value], str) or
             annot[AnnotationGeneralKeys.DELIMITER.value].upper() not in [e.name for e in AnnotationDelimiter]):
        raise KeyError(f"'{AnnotationGeneralKeys.DELIMITER.value}' key is not valid or is not a string.")

    # Columns key
    if AnnotationGeneralKeys.COLUMNS.value in annot and \
            not isinstance(annot[AnnotationGeneralKeys.COLUMNS.value], list):
        raise KeyError(f"'{AnnotationGeneralKeys.COLUMNS.value}' key is not a list.")

    # Annotations key
    if AnnotationGeneralKeys.ANNOTATION.value in annot and \
            not isinstance(annot[AnnotationGeneralKeys.ANNOTATION.value], list):
        raise KeyError(f"'{AnnotationGeneralKeys.ANNOTATION.value}' key is not a list.")

    # Excludes key
    if AnnotationGeneralKeys.EXCLUDE.value in annot and \
            (not isinstance(annot[AnnotationGeneralKeys.EXCLUDE.value], list) or
             not all([ExcludesKeys.FIELD.value in x and ExcludesKeys.VALUE.value in x
                      for x in annot[AnnotationGeneralKeys.EXCLUDE.value]])):
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

    # Value key
    # if (annot[AnnotationKeys.TYPE.value] == AnnotationTypes.STATIC.value or
    #    annot[AnnotationKeys.TYPE.value] == AnnotationTypes.INTERNAL.value) and \
    #        not isinstance(annot[AnnotationKeys.VALUE.value], str):
    #    raise KeyError(f"'{AnnotationKeys.VALUE.value}' key not found or is not a str.")

    # Field source key
    if (annot[AnnotationKeys.TYPE.value] == AnnotationTypes.INTERNAL.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.PLUGIN.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.MAPPING.value) and \
            AnnotationKeys.FIELD_SOURCE.value in annot and \
            not isinstance(annot[AnnotationKeys.FIELD_SOURCE.value], list):
        raise KeyError(f"'{AnnotationKeys.FIELD_SOURCE.value}' key not found or is not a list.")

    # Dirname and filename key
    if (annot[AnnotationKeys.TYPE.value] == AnnotationTypes.DIRNAME.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.FILENAME.value or
        annot[AnnotationKeys.TYPE.value] == AnnotationTypes.INTERNAL.value) and \
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
    if annot[AnnotationKeys.TYPE.value] == AnnotationTypes.MAPPING.value and \
            (AnnotationKeys.FIELD_SOURCE.value not in annot or
             AnnotationKeys.FIELD_MAPPING.value not in annot or
             AnnotationKeys.FILE_MAPPING.value not in annot or
             AnnotationKeys.FIELD_VALUE.value not in annot or
             not isinstance(annot[AnnotationKeys.FIELD_SOURCE.value], list) or
             not isinstance(annot[AnnotationKeys.FIELD_MAPPING.value], str) or
             not isinstance(annot[AnnotationKeys.FILE_MAPPING.value], str) or
             not isinstance(annot[AnnotationKeys.FIELD_VALUE.value], str)):
        raise KeyError(f"'{AnnotationTypes.MAPPING.value}' not annotated well.")


class Annotation:
    """A representation of the schema that files will be parsed"""
    _builders: dict = {}

    def __init__(self, path: str) -> None:
        """
        Inits Annotation with annotation file path.

        Parameters
        ---------
        path : str
            A string path where Annotation file is located.
        """
        self._builders: dict = {}

        self._register_builders()
        self._path = path
        raw_annotation = _read_annotation_file(path)
        _check_general_keys(raw_annotation)
        for annot in raw_annotation.get(AnnotationGeneralKeys.ANNOTATION.value, []):
            _check_annotation_keys(annot)

        patterns = raw_annotation[AnnotationGeneralKeys.PATTERN.value]
        self._patterns = patterns if isinstance(patterns, List) else [patterns]
        self._recursive = raw_annotation.get(AnnotationGeneralKeys.RECURSIVE.value, True)
        self._delimiter = raw_annotation.get(AnnotationGeneralKeys.DELIMITER.value, DEFAULT_DELIMITER).upper()
        self._columns = raw_annotation.get(AnnotationGeneralKeys.COLUMNS.value, DEFAULT_COLUMNS)

        self._format = raw_annotation.get(AnnotationGeneralKeys.FORMAT.value, DEFAULT_FORMAT).replace('.', '')
        self._excludes = raw_annotation.get(AnnotationGeneralKeys.EXCLUDE.value, [])

        self._annotations: dict = {}
        for k in raw_annotation.get(AnnotationGeneralKeys.ANNOTATION.value, []):
            self._annotations[k[AnnotationKeys.FIELD.value]] = \
                AnnotationTypesBuilders[k[AnnotationKeys.TYPE.value].upper()].value(k, self._path)

        self._check_columns()

    def _register_builders(self) -> None:
        for b in AnnotationTypes:
            self._builders[b.value] = AnnotationTypesBuilders[b.name].value

    def _check_columns(self) -> None:
        for col in self._columns:
            if col not in self._annotations:
                raise KeyError(f"'{col}' column unable to find.")

    @property
    def patterns(self) -> List[str]:
        """List[str]: files patterns that annotation will match"""
        return self._patterns

    @property
    def format(self) -> str:
        """str: output format that will have parsed files"""
        return self._format

    @property
    def delimiter(self) -> str:
        """str: delimiter that annotation will read on files"""
        return self._delimiter

    @property
    def columns(self) -> List:
        """List: columns that will appear on parsed output files"""
        return self._columns

    @property
    def annotations(self) -> dict:
        """dict: annotation that will cover Annotation object"""
        return self._annotations

    @property
    def excludes(self) -> List:
        """List: values that will be excluded after the parsing"""
        return self._excludes

    @property
    def structure(self) -> dict:
        """dict: general structure of Annotation schema"""
        structure_aux = {AnnotationGeneralKeys.ANNOTATION.name: self._annotations,
                         AnnotationGeneralKeys.EXCLUDE.name: self._excludes}
        return {e: structure_aux for e in self._patterns}
