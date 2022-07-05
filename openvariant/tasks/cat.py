"""
Cat  task
====================================
A core functionality to execute cat task.
"""
from typing import List

from openvariant.annotation.config_annotation import AnnotationFormat
from openvariant.find_files.find_files import find_files
from openvariant.variant.variant import Variant


def _format_line(line: List[str], out_format: str) -> str:
    """Line formatting for output"""
    return AnnotationFormat[out_format.upper()].value.join(line)


def cat(base_path: str, annotation_path: str or None = None, where: str = None, header_show: bool = True,
        output: str or None = None) -> None:
    """Print on the stdout/"output" the parsed files.

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
    output : str or None
        Save output on a file.
    """
    out_file = None
    if output:
        out_file = open(output, "w")
    for file, annotation in find_files(base_path, annotation_path):
        result = Variant(file, annotation)
        header = result.header
        if header_show:
            if output:
                out_file.write(_format_line(header, result.annotation.format))
                out_file.write("\n")
            else:
                print(_format_line(header, result.annotation.format))
            header_show = False
        for i, r in enumerate(result.read(where=where)):
            if isinstance(r, dict):
                if output:
                    out_file.write(_format_line(list(map(str, r.values())), result.annotation.format))
                    out_file.write("\n")
                else:
                    print(_format_line(list(map(str, r.values())), result.annotation.format))
    if output:
        out_file.close()
