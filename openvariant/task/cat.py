from openvariant.find.find import find_files
from openvariant.utils.format_line import format_line
from openvariant.utils.where import parse_where, skip
from openvariant.variant.variant import Variant


def cat(base_path: str, annotation_path: str or None, where: str = None, header_show: bool = True) -> None:
    for file, annotation in find_files(base_path, annotation_path):
        where_clauses = parse_where(where)
        result = Variant(base_path, annotation)
        header = result.header if len(annotation.columns) == 0 else annotation.columns
        if header_show:
            print(format_line(header, result.annotation.format))
            header_show = False
        for i, r in enumerate(result.read()):
            if isinstance(r, dict):
                if skip(r, where_clauses):
                    continue
                print(format_line(list(map(str, r.values())), result.annotation.format))


