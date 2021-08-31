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


