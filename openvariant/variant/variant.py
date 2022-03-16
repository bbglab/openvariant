"""
Variant
====================================
A core class to represent the files that will be parsed by an Annotation file.
"""

import csv
import ctypes
import gzip
import lzma
from fnmatch import fnmatch
from functools import lru_cache
import mmap
from os.path import isdir, isfile
import re
from typing import Generator, List, Callable, Any

from openvariant.annotation.annotation import Annotation
from openvariant.annotation.builder import MappingBuilder
from openvariant.annotation.process import AnnotationTypesProcess
from openvariant.config.config_annotation import AnnotationFormat, AnnotationTypes, AnnotationDelimiter


def _open_file(file_path: str, mode='r+b'):
    """Open raw files or compressed files"""

    if file_path.endswith('xz'):
        open_method = lzma.open
        file = open_method(file_path, mode)
        mm = file
    else:
        open_method = open
        file = open_method(file_path, mode)
        mm: mmap = mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_READ)

    return mm, file


def _base_parser(mm_obj: mmap, file_path: str, delimiter: str) -> Generator[int, str, None]:
    """Cleaning comments and irrelevant data"""
    try:
        if file_path.endswith('gz') or file_path.endswith('bgz'):
            mm_obj = gzip.GzipFile(mode="r+b", fileobj=mm_obj)
    except KeyError:
        raise KeyError(f"'{delimiter}' key not found.")

    for l_num, line in enumerate(iter(mm_obj.readline, b'')):
        line = line.decode('utf-8')
        row_line = line.split(AnnotationDelimiter[delimiter].value)
        row_line = list(map(lambda w: w.replace("\n", ""), row_line))

        if len(row_line) == 0:
            continue

        # Skip comments
        if (row_line[0].startswith('#') or row_line[0].startswith('##') or row_line[0].startswith('browser') or
            row_line[0].startswith('track')) and not row_line[0].startswith('#CHROM'):
            continue

        yield l_num, row_line


def _exclude(line: dict, excludes: dict) -> bool:
    """Excludes values described on the annotation file"""
    for k, v in excludes.items():
        for val in v:
            if val is not None and val.startswith("!"):
                valp = val.replace("!", "")
                if line[k] != valp:
                    return True
            elif line[k] == val:
                return True

    return False


def _extract_header(file_path: str, original_header: list, annotation: Annotation):
    """Extract header to parse the entire file, and create a reference for each field"""
    header_schema = {}
    mapping_fields = []

    for field, ann in annotation.annotations.items():
        ann_type = ann[0]
        if ann_type == AnnotationTypes.MAPPING.value:
            mapping_fields.append((field, ann))
        else:
            header_schema.update({field: AnnotationTypesProcess[ann_type].value(ann, original_header, file_path,
                                                                                header_schema)})

    for field, ann in mapping_fields:
        ann_type = ann[0]
        header_schema.update({field: AnnotationTypesProcess[ann_type].value(ann, original_header, file_path,
                                                                            header_schema)})
    return header_schema, annotation.columns


@lru_cache(maxsize=256)
def _parse_field(value: float or int or str, func: Callable) -> str:
    """Getting the value of a specific annotation field. Cached with LRU policy"""
    result = func(value)
    return result if result is not None else str(float('nan'))


def _parse_plugin_field(row: dict, field_name: str, file_path: str, value: Any, func: Callable) -> str:
    """Getting the value of a specific plugin annotation. No cached"""
    ctxt = value(row, field_name, file_path)
    return func(ctxt)


def _parse_mapping_field(x: MappingBuilder, row: dict, func: Callable):
    """Getting the value of a specific mapping annotation. No cached"""
    if x[1] is None:
        raise ValueError(f'Wrong source fields on {x[0]} annotation')
    value = None
    for source in x[1]:
        try:
            map_key = row[source]
            value = x[2].get(map_key, None)
        except KeyError:
            pass
    return str(value) if value is not None else str(float('nan'))


def _parser(file_path: str, annotation: Annotation, group_by: str, display_header: bool) \
        -> Generator[dict, None, None]:
    """Parsing of an entire file with annotation schema"""
    header, row, row_header = None, {}, []
    mm, file = _open_file(file_path, "rb")
    for lnum, line in _base_parser(mm, file_path, annotation.delimiter):
        if header is None:
            header, row_header = _extract_header(file_path, line, annotation)
            if not display_header:
                continue
            row = row_header
            yield row
        else:
            try:
                line_dict = {}
                row, plugin_values, mapping_values = {}, {}, {}
                for head in annotation.annotations.keys():
                    type_ann, value, func = header[head]
                    if type_ann == AnnotationTypes.PLUGIN.name:
                        plugin_values[head] = header[head]
                    elif type_ann == AnnotationTypes.MAPPING.name:
                        mapping_values[head] = header[head]
                    elif type_ann == AnnotationTypes.INTERNAL.name:
                        value = line[value] if value is not None else None
                        line_dict[head] = _parse_field(value, func)
                    else:
                        line_dict[head] = _parse_field(value, func)

                for head, mapping in mapping_values.items():
                    _, builder_mapping, func = mapping
                    line_dict[head] = _parse_mapping_field(builder_mapping, line_dict, func)
                for head, plug in plugin_values.items():
                    _, ctxt_plugin, func_plugin = plug
                    line_dict[head] = _parse_plugin_field(line_dict, head, file_path, ctxt_plugin, func_plugin)

                for k in annotation.columns:
                    row[k] = line_dict[k].format(**line_dict)

                if group_by is not None and group_by not in annotation.columns:
                    try:
                        row[group_by] = line_dict[group_by].format(**line_dict)
                    except KeyError as e:
                        raise KeyError(f"Unable to find group by: {e}. Check annotation for {file_path} file")

                if row and not _exclude(line_dict, annotation.excludes):
                    yield row

            except (ValueError, IndexError, KeyError) as e:
                mm.close()
                file.close()
                raise ValueError(f"Error parsing line: {lnum} {file_path}: {e}")
    mm.close()
    file.close()


def _check_extension(ext: str, path: str) -> bool:
    """Check if file matches with the annotation pattern"""
    if ext[0] == '*':
        match = fnmatch(path, ext)
    else:
        reg_apply = re.compile(ext + '$')
        match = len(reg_apply.findall(path)) != 0
    return match


def _unify(base_path: str, annotation: Annotation, group_by: str = None, display_header: bool = True) \
        -> Generator[dict, None, None]:
    """Parse all the files thought the annotation schema and generated yields to interrate"""
    for x in _parser(base_path, annotation, group_by, display_header):
        yield x


class Variant:
    """A representation of parsed files

        Methods
        -------
        read(group_key: str or None = None)
            Read the parsed files with its proper annotation.
        save(file_path: str, display_header: bool = True)
            Save parsed files on specified location.
    """

    def __init__(self, path: str, annotation: Annotation) -> None:
        """
        Inits Variant with files path and Annotation object

        Parameters
        ---------
        path : str
            A string path where files to parse are located (could be directory or a single file).
        annotation : Annotation
            Object to describe the schema of parsed files.
        """
        if path is None or path == '' or not isfile(path):
            raise ValueError('Invalid path, must be a file')
        if annotation is None:
            raise ValueError('Invalid annotation')

        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
        self._path: str = path
        self._annotation: Annotation = annotation
        self._header: List[str] = list(annotation.annotations.keys()) if len(annotation.columns) == 0 \
            else annotation.columns

    @property
    def path(self) -> str:
        """str: Path where parsed files are located"""
        return self._path

    @property
    def header(self) -> List[str]:
        """List[str]: Header of the corresponding parsed files"""
        return self._header

    @property
    def annotation(self) -> Annotation:
        """Annotation: Annotation object which files were parsed"""
        return self._annotation

    def read(self, group_key: str or None = None) -> Generator[dict, None, None]:
        """
        Read parsed files and generated an iterator for each row

        Parameters
        ---------
        group_key : str or None
            A string that indicates how rows will be grouped (optional).

        Yields
        ------
        dict
            Representation of a parsed row.
        """
        for i, line in enumerate(_unify(self._path, self._annotation, group_by=group_key)):
            if i != 0:
                yield line

    def save(self, file_path: str, display_header: bool = True) -> None:
        """
        Save parsed files in an indicated location.

        Parameters
        ---------
        file_path : str or None
            A string that indicates the location to store the output file.

        display_header : bool
            A bool that indicates if the output will have header or not (optional).
        """
        if file_path is None or isdir(file_path):
            raise ValueError("The path must be a file.")
        with open(file_path, "w") as file:
            writer = csv.writer(file, delimiter=AnnotationFormat[self._annotation.format.upper()].value)
            for i, line in enumerate(_unify(self._path, self._annotation)):
                if display_header and i == 0:
                    writer.writerow(line)
                elif i != 0:
                    writer.writerow(line.values())
