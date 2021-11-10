import csv
import gzip
import lzma
from os import listdir
from os.path import isfile, join, isdir
import re
from typing import Generator, TextIO, List

from openvariant.annotation.annotation import Annotation
from openvariant.annotation.parser import AnnotationTypesParsers
from openvariant.config.config_annotation import AnnotationFormat, AnnotationGeneralKeys, ExcludesKeys, \
    AnnotationDelimiter, AnnotationTypes
from openvariant.utils.logger import log


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
    for k, v in annotations.items():
        try:
            value = float('nan')
            if v[0] != AnnotationTypes.MAPPING.name:
                value = AnnotationTypesParsers[v[0]].value(v, line, original_header, path)
            else:
                remain_annotation[k] = v
            row_parser.append(value)
        except IndexError:
            row_parser.append(float('nan'))

    row_parser = list(map(str, row_parser))
    dict_line = {h: row_parser[i] for i, h in enumerate(header)}

    for k, v in remain_annotation.items():
        dict_line[k] = AnnotationTypesParsers[v[0]].value(v, line, original_header, path, dict_line)

    for k, v in dict_line.items():
        dict_line[k] = v.format(**dict_line)

    return dict_line


def _parser(file: str, annotation: dict, format_output: str, delimiter: str, display_header=True) -> \
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
                log.error(f"Error parsing header {e}")
        else:
            try:
                row = _parse_row(annotation, line, header, original_header, file)
            except (ValueError, IndexError) as e:
                log.error(f"Error parsing line {lnum} {file} ({e, line, header})")
                continue

        yield row
    fd.close()


def _check_extension(ext: str, path: str) -> re.Match:
    rext = re.compile(ext[-1:] + "$")
    return rext.search(path)


def _extract_header(annotation: Annotation):
    return list(annotation.annotations.keys())


class Variant:

    def __init__(self, path: str, ann: Annotation) -> None:
        self._path: str = path
        self._annotation: Annotation = ann
        self._header: List[str] = _extract_header(ann)
        self._generator: Generator[dict, None, None] = self._unify(path, ann)

    def _unify(self, base_path: str, annotation: Annotation, display_header=True) -> Generator[dict, None, None]:
        an = annotation.structure
        format_output = annotation.format
        if isfile(base_path):
            for ext, ann in an.items():
                if _check_extension(ext, base_path):
                    for x in _parser(base_path, ann, format_output, annotation.delimiter, display_header):
                        display_header = False
                        yield x
        else:
            try:
                for file in listdir(base_path):
                    file_path = join(base_path, file)
                    if isfile(file_path):
                        for ext, ann in an.items():
                            if _check_extension(ext, file_path):
                                for x in _parser(file_path, ann, format_output, annotation.delimiter, display_header):
                                    display_header = False
                                    yield x
                    else:
                        for x in self._unify(file_path, annotation, display_header):
                            display_header = False
                            yield x
            except PermissionError as e:
                print(e)

    def _apply_exclude(self, line: dict) -> bool:
        for exclude in self._annotation.excludes:
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

    def read(self) -> Generator[dict, None, None]:
        for i, line in enumerate(self._generator):
            if i != 0:
                if self._apply_exclude(line):
                    continue
                yield line

    def save(self, file_path: str, display_header=True):
        if isdir(file_path):
            raise ValueError("The path must be a file.")
        with open(file_path, "w") as file:
            writer = csv.writer(file, delimiter=AnnotationFormat[self._annotation.format.upper()].value)
            for i, line in enumerate(self._generator):
                if display_header and i == 0:
                    writer.writerow(line)
                elif i != 0:
                    if self._apply_exclude(line):
                        continue
                    writer.writerow(line)
            file.close()

    @property
    def path(self) -> str:
        return self._path

    @property
    def header(self) -> List[str]:
        return self._header

    @property
    def generator(self) -> Generator[dict, None, None]:
        return self._generator

    @property
    def annotation(self) -> Annotation:
        return self._annotation
