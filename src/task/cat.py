from typing import Generator

from src.annotation.annotation import Annotation
from src.utils.where import parse_where, skip
from src.variant.variant import Variant


def cat(base_path: str, annotation_path: str, where=None) -> Generator[str, None, None]:
    ann = Annotation(annotation_path)
    where_clauses = parse_where(where)

    result = Variant(base_path, ann)
    header = result.header
    for r in result.read(False):
        if skip(r, header, where_clauses):
            continue
        yield r
