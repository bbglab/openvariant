from os import listdir
from os.path import isfile, join
import re
from typing import Generator, TextIO, List

from src.annotation.annotation import Annotation
from src.annotation.parser import AnnotationTypesParsers
from src.config.config_annotation import AnnotationFormat, AnnotationGeneralKeys
from src.utils.logger import log


def _base_parser(lines: TextIO) -> Generator[int, str, None]:
    for l_num, line in enumerate(lines, start=1):
        # Skip empty lines
        if len(line) == 0:
            continue

        # Skip comments
        if (line.startswith('#') or line.startswith('##') or line.startswith('browser') or line.startswith('track') ) \
                and not line.startswith('#CHROM'):
            continue

        yield l_num, line


def _parse_row(ann: dict, line: List, original_header: List, path: str, format_output: str) -> str:
    annotations_header = ann[AnnotationGeneralKeys.ANNOTATION.name]
    row_parser = []
    for k, v in annotations_header.items():
        row_parser.append(AnnotationTypesParsers[v[0]].value(v, line, original_header, path))
    return AnnotationFormat[format_output.upper()].value.join(list(map(str, row_parser)))


def _parser(file: str, annotation: dict, format_output: str, display_header=True) -> Generator[str, None, None]:
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
                row = AnnotationFormat[format_output.upper()].value.join(header)
            except (ValueError, KeyError) as e:
                log.warning("Error parsing header (%s)", e)
        else:
            try:
                row = _parse_row(annotation, line.split(), original_header, file, format_output)
            except (ValueError, IndexError) as e:
                log.warning("Error parsing line %d %s (%s %s %s)", lnum, file, e, line, header)
                continue

        yield row


def _check_extension(ext: str, path: str) -> re.Match:
    rext = re.compile(ext + "$")
    return rext.search(path)


def unify(base_path: str, annotation: Annotation, display_header=True) -> Generator[str, None, None]:
    an = annotation.structure
    format_output = annotation.format
    if isfile(base_path):
        for ext, ann in an.items():
            if _check_extension(ext, base_path):
                for x in _parser(base_path, ann, format_output, display_header):
                    display_header = False
                    yield x

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
                for x in unify(file_path, annotation, display_header):
                    display_header = False

                    yield x
    except PermissionError as e:
        print(e)
