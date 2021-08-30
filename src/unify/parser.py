from typing import TextIO, Generator, List

from src.annotation.parser import AnnotationTypesParsers
from src.config.config_annotation import AnnotationGeneralKeys, AnnotationFormat
from src.utils.logger import log


def _head(line, schema=None, extra=None, required=None):
    header = True
    extra_header = []
    inferred_header = []
    for i, h in enumerate(line):
        print(h)
    '''
        known = __known_headers(h, schema)
        if len(known) > 0:
            for field, method in known:
                header.append((field, method, i))
        extra_header.append((h, str, i))

    inferred_header = len(header) == 0
    if inferred_header:
        # TODO Infer the header from the values of the first line
        raise NotImplementedError("We need a header")

    if extra is not None:

        # TODO Check header collision
        if isinstance(extra, list):
            header += [h for h in extra_header if h[0] in extra]
        else:
            header += extra_header

    if required is not None and not (set(required) <= set([h[0] for h in header])):
        raise SyntaxError('Missing fields in file header. Required fields: {}'.format(required))
    '''
    return header, inferred_header


def _base_parser(lines: TextIO, count: bool) -> Generator[int, str, None]:
    for l_num, line in enumerate(lines, start=1):
        # Skip empty lines
        if len(line) == 0:
            continue

        # Skip comments
        if line.startswith('#') and not line.startswith('#CHROM'):
            continue

        # Parse columns
        # if not count:
        #    line = [v.strip() for v in line.split('\t')]

        yield l_num, line


def _parse_row(ann: dict, line: List, original_header: List, path: str, format_output: str) -> str:
    annotations_header = ann[AnnotationGeneralKeys.ANNOTATION.name]
    row_parser = []
    for k, v in annotations_header.items():
        row_parser.append(AnnotationTypesParsers[v[0]].value(v, line, original_header, path))
    return AnnotationFormat[format_output.upper()].value.join(list(map(str, row)))


def parser(file: str, annotation: dict, format_output: str) -> Generator[str, None, None]:
    row = None
    fd = open(file, "rt")

    header = list(annotation[AnnotationGeneralKeys.ANNOTATION.name].keys())
    original_header = None
    for lnum, line in _base_parser(fd, False):
        if original_header is None:
            original_header = line.split()
            try:
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
