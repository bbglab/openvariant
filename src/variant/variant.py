import csv
from os import listdir
from os.path import isfile, join, isdir
import re
from typing import Generator, TextIO, List

from src.annotation.annotation import Annotation
from src.annotation.parser import AnnotationTypesParsers
from src.config.config_annotation import AnnotationFormat, AnnotationGeneralKeys, ExcludesKeys
from src.utils.logger import log


def _base_parser(lines: TextIO) -> Generator[int, str, None]:
    for l_num, line in enumerate(lines, start=1):
        # Skip empty lines
        if len(line) == 0:
            continue

        # Skip comments
        if (line.startswith('#') or line.startswith('##') or line.startswith('browser') or line.startswith('track')) \
                and not line.startswith('#CHROM'):
            continue

        yield l_num, line


def _parse_row(ann: dict, line: List, original_header: List, path: str, format_output: str) -> List[str]:
    annotations = ann[AnnotationGeneralKeys.ANNOTATION.name]
    row_parser = []
    for k, v in annotations.items():
        try:
            row_parser.append(AnnotationTypesParsers[v[0]].value(v, line, original_header, path))
        except IndexError:
            row_parser.append(float('nan'))

    return list(map(str, row_parser))


def _parser(file: str, annotation: dict, format_output: str, display_header=True) -> Generator[List[str], None, None]:
    row = None
    fd = open(file, "rt")

    header = list(annotation[AnnotationGeneralKeys.ANNOTATION.name].keys())
    original_header = None
    for lnum, line in _base_parser(fd):
        if original_header is None:
            original_header = line.split()
            try:
                if not display_header:
                    continue
                row = header
            except (ValueError, KeyError) as e:
                log.error(f"Error parsing header {e}")
        else:
            try:
                row = _parse_row(annotation, line.split(), original_header, file, format_output)
            except (ValueError, IndexError) as e:
                log.error(f"Error parsing line {lnum} {file} ({e, line, header})")
                continue

        yield row


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
        self._generator: Generator[List[str], None, None] = self._unify(path, ann)

    def _unify(self, base_path: str, annotation: Annotation, display_header=True) -> Generator[List[str], None, None]:
        an = annotation.structure
        format_output = annotation.format
        if isfile(base_path):
            for ext, ann in an.items():
                if _check_extension(ext, base_path):
                    for x in _parser(base_path, ann, format_output, display_header):
                        display_header = False
                        yield x
        else:
            try:
                for file in listdir(base_path):
                    file_path = join(base_path, file)
                    if isfile(file_path):
                        for ext, ann in an.items():
                            if _check_extension(ext, file_path):
                                for x in _parser(file_path, ann, format_output, display_header):
                                    display_header = False
                                    yield x
                    else:
                        for x in self._unify(file_path, annotation, display_header):
                            display_header = False
                            yield x
            except PermissionError as e:
                print(e)

    def _apply_exclude(self, line: List[str]) -> bool:
        for exclude in self._annotation.excludes:
            try:
                i = self._header.index(exclude[ExcludesKeys.FIELD.value])

                if str(exclude[ExcludesKeys.VALUE.value]) == line[i]:
                    return True
            except (KeyError, ValueError):
                return False
        return False

    def _format_line(self, line) -> str:
        return AnnotationFormat[self._annotation.format.upper()].value.join(line)

    def read(self, display_header=True) -> Generator[str, None, None]:
        for i, line in enumerate(self._generator):
            if display_header and i == 0:
                yield line
            elif i != 0:
                if self._apply_exclude(line):
                    continue
                yield self._format_line(line)

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
    def path(self):
        return self._path

    @property
    def header(self):
        return self._header
