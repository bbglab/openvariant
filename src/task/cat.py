from src.annotation.annotation import Annotation
from src.utils.format_line import format_line
from src.utils.where import parse_where, skip
from src.variant.variant import Variant


def cat(base_path: str, annotation_path: str, where=None) -> None:
    ann = Annotation(annotation_path)
    where_clauses = parse_where(where)

    result = Variant(base_path, ann)
    header = result.header
    print(format_line(header, result.annotation.format))
    for r in result.read():
        if skip(r, where_clauses):
            continue
        print(format_line(list(r.values()), result.annotation.format))