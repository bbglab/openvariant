from openvariant.annotation.annotation import Annotation
from openvariant.utils.format_line import format_line
from openvariant.utils.where import parse_where, skip
from openvariant.variant.variant import Variant


def cat(base_path: str, annotation_path: str, where=None) -> None:
    ann = Annotation(annotation_path)
    where_clauses = parse_where(where)

    result = Variant(base_path, ann)
    header = result.header if len(ann.columns) == 0 else ann.columns
    print(format_line(header, result.annotation.format))
    for i, r in enumerate(result.read()):
        if skip(r, where_clauses):
            continue
        print(format_line(list(map(str, r.values())), result.annotation.format))