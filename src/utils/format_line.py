from typing import List

from src.config.config_annotation import AnnotationFormat


def format_line(line: List[str], out_format: str) -> str:
    return AnnotationFormat[out_format.upper()].value.join(line)
