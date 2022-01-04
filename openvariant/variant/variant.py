"""
Variant
====================================
A core class to represent the files that will be parsed by an Annotation file.
"""

import csv
import ctypes
import gzip
import lzma
from fnmatch import fnmatch
from os import listdir
from os.path import isfile, join, isdir
import re
from typing import Generator, TextIO, List

from openvariant.annotation.annotation import Annotation
from openvariant.annotation.parser import AnnotationTypesParsers
from openvariant.config.config_annotation import AnnotationFormat, AnnotationGeneralKeys, ExcludesKeys, \
    AnnotationDelimiter, AnnotationTypes


def _open_file(file_path: str, mode='rt') -> TextIO:
    open_method = open
    if file_path.endswith('gz') or file_path.endswith('bgz'):
        open_method = gzip.open
    elif file_path.endswith('xz'):
        open_method = lzma.open

    return open_method(file_path, mode)


def _base_parser(lines: TextIO, delimiter: str) -> Generator[int, str, None]:
    try:
        read_tsv = csv.reader(lines, delimiter=AnnotationDelimiter[delimiter].value)
    except KeyError:
        raise KeyError(f"'{delimiter}' key not found.")
    for l_num, line in enumerate(read_tsv):  # lines, start=1):
        # Skip empty lines
        if len(line) == 0:
            print(line)
            continue

        # Skip comments
        if (line[0].startswith('#') or line[0].startswith('##') or line[0].startswith('browser') or line[0].startswith(
                'track')) \
                and not line[0].startswith('#CHROM'):
            continue

        yield l_num, line


def _parse_row(ann: dict, line: List, header: List, original_header: List, path: str) -> dict:
    annotations = ann[AnnotationGeneralKeys.ANNOTATION.name]
    row_parser = []
    remain_annotation = {}
    annot_plugins = []
    for k, v in annotations.items():
        try:
            value = float('nan')
            if v[0] == AnnotationTypes.PLUGIN.name:
                annot_plugins.append(v)
            elif v[0] != AnnotationTypes.MAPPING.name:
                value = AnnotationTypesParsers[v[0]].value(v, line, original_header, path)
            else:
                remain_annotation[k] = v
            row_parser.append(value)
        except IndexError:
            row_parser.append(float('nan'))

    row_parser = list(map(str, row_parser))
    dict_line = {h: row_parser[i] for i, h in enumerate(header)}

    for v in annot_plugins:
        dict_line = AnnotationTypesParsers[v[0]].value(v, line, original_header, path, dict_line)

    for k, v in remain_annotation.items():
        dict_line[k] = AnnotationTypesParsers[v[0]].value(v, line, original_header, path, dict_line)

    try:
        for k, v in dict_line.items():
            dict_line[k] = v.format(**dict_line)
    except AttributeError as e:
        raise AttributeError(f'Parsing annotations error for {dict_line}: {e}')

    return dict_line


def _apply_exclude(line: dict, excludes: List) -> bool:
    for exclude in excludes:
        try:
            value_line = line[exclude[ExcludesKeys.FIELD.value]]
            value_exclude = str(exclude[ExcludesKeys.VALUE.value])
            if value_exclude.startswith("!"):
                if value_line != value_exclude[1::]:
                    return True
            else:
                if value_line == value_exclude:
                    return True
        except (KeyError, ValueError):
            return False
    return False


def _parser(file: str, annotation: dict, delimiter: str, columns: List, excludes: List, group_by=None,
            display_header=True) -> \
        Generator[dict, None, None]:
    row = None
    fd = _open_file(file, "rt")

    header = list(annotation[AnnotationGeneralKeys.ANNOTATION.name].keys())
    original_header = None
    for lnum, line in _base_parser(fd, delimiter):
        if original_header is None:
            original_header = line
            try:
                if not display_header:
                    continue
                row = header

            except (ValueError, KeyError) as e:
                ValueError(f"Error parsing header {e}")
        else:
            try:
                row = _parse_row(annotation, line, header, original_header, file)

                row_aux = {}
                if _apply_exclude(row, excludes):
                    continue

                if len(columns) != 0:
                    if group_by is not None and group_by not in columns:
                        try:
                            row_aux[group_by] = row[group_by]
                        except KeyError as e:
                            raise KeyError(f"Unable to find group by: {e}. Check annotation for {file} file")

                    for col in columns:
                        row_aux[col] = row[col]

                    row = row_aux
            except (ValueError, IndexError, KeyError) as e:
                raise ValueError(f"Error parsing line: {lnum} {file}: {e}")

        yield row
    fd.close()


def _check_extension(ext: str, path: str) -> bool:
    if ext[0] == '*':
        match = fnmatch(path, ext)
    else:
        reg_apply = re.compile(ext + '$')
        match = len(reg_apply.findall(path)) != 0
    return match


def _extract_header(annotation: Annotation):
    return list(annotation.annotations.keys())


class Variant:
    """A representation of parsed files"""

    def __init__(self, path: str, annotation: Annotation) -> None:
        """
        Inits Variant with files path and Annotation object

        Parameters
        ---------
        path : str
            A string path where files to parse are located (could be directory or a single file).
        annotation : Annotation
            Object to describe the schema of parsed files.
        """
        if path is None or path == '' or annotation is None:
            raise ValueError('Invalid path or wrong Annotation')

        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
        self._path: str = path
        self._annotation: Annotation = annotation
        self._header: List[str] = _extract_header(annotation)

    @property
    def path(self) -> str:
        """str: Path where parsed files are located"""
        return self._path

    @property
    def header(self) -> List[str]:
        """List[str]: Header of the corresponding parsed files"""
        return self._header

    @property
    def annotation(self) -> Annotation:
        """Annotation: Annotation object which files were parsed"""
        return self._annotation

    def _unify(self, base_path: str, annotation: Annotation, group_by=None, display_header=True) \
            -> Generator[dict, None, None]:
        an = annotation.structure
        if isfile(base_path):
            for ext, ann in an.items():
                if _check_extension(ext, base_path):
                    for x in _parser(base_path, ann, annotation.delimiter, annotation.columns, annotation.excludes,
                                     group_by, display_header):
                        display_header = False
                        yield x
        else:
            try:
                for file in listdir(base_path):
                    file_path = join(base_path, file)
                    if isfile(file_path):
                        for ext, ann in an.items():
                            if _check_extension(ext, file_path):
                                for x in _parser(file_path, ann, annotation.delimiter, annotation.columns,
                                                 annotation.excludes,
                                                 group_by, display_header):
                                    display_header = False
                                    yield x
                    else:
                        for x in self._unify(file_path, annotation, display_header=display_header):
                            display_header = False
                            yield x
            except PermissionError as e:
                raise PermissionError(f"Unable to open a file, permission issue: {e}")

    def read(self, group_key: str or None = None) -> Generator[dict, None, None]:
        """
        Read parsed files and generated an iterator for each row

        Parameters
        ---------
        group_key : str or None
            A string that indicates how rows will be grouped (optional).

        Yields
        ------
        dict
            Representation of a parsed row.
        """
        for i, line in enumerate(self._unify(self._path, self._annotation, group_by=group_key)):
            if i != 0:
                yield line

    def save(self, file_path: str, display_header: bool = True) -> None:
        """
        Save parsed files in an indicated location.

        Parameters
        ---------
        file_path : str or None
            A string that indicates the location to store the output file.

        display_header : bool
            A bool that indicates if the output will have header or not (optional).
        """
        if file_path is None or isdir(file_path):
            raise ValueError("The path must be a file.")
        with open(file_path, "w") as file:
            writer = csv.writer(file, delimiter=AnnotationFormat[self._annotation.format.upper()].value)
            for i, line in enumerate(self._unify(self._path, self._annotation)):
                if display_header and i == 0:
                    writer.writerow(line)
                elif i != 0:
                    writer.writerow(line.values())
