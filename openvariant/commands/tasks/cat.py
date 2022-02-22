"""
Cat  task
====================================
A core functionality to execute cat task.
"""
from typing import List

from openvariant.config.config_annotation import AnnotationFormat
from openvariant.find.find import find_files
from openvariant.utils.where import parse_where, skip
from openvariant.variant.variant import Variant


def _format_line(line: List[str], out_format: str) -> str:
    """Line formatting for output"""
    return AnnotationFormat[out_format.upper()].value.join(line)


def cat(base_path: str, annotation_path: str or None = None, where: str = None, header_show: bool = True) -> None:
    """Print on the stdout the parsed files.

    It will parse the input files with its proper annotation schema, and it'll show the result on the stdout.
    It can be printed with or without header. Can be added a 'where' expression.

    Parameters
    ----------
    base_path : srt
        Base path of input files.
    annotation_path : str or None
        Path of annotation file.
    where : str
        Conditional statement.
    header_show : bool
        Shows header on the output.
    """
    for file, annotation in find_files(base_path, annotation_path):
        where_clauses = parse_where(where)
        result = Variant(file, annotation)
        header = result.header
        if header_show:
            print(_format_line(header, result.annotation.format))
            header_show = False
        for i, r in enumerate(result.read()):
            if isinstance(r, dict):
                if skip(r, where_clauses):
                    continue
                print(_format_line(list(map(str, r.values())), result.annotation.format))
