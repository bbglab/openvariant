import csv
from os import listdir
from os.path import isfile, join, isdir
import re
from typing import Generator, TextIO, List

from src.annotation.annotation import Annotation
from src.annotation.parser import AnnotationTypesParsers
from src.config.config_annotation import AnnotationFormat, AnnotationGeneralKeys
from src.task.find import find_files
from src.utils.logger import log


def _base_parser(lines: TextIO) -> Generator[int, str, None]:
    for l_num, line in enumerate(lines, start=1):
        # Skip empty lines
        if len(line) == 0:
            continue

        # Skip comments
        if (line.startswith('#') or line.startswith('##') or line.startswith('browser') or line.startswith('track')) \
                and not line.startswith('#CHROM'):
            continue

        yield l_num, line


def _parse_row(ann: dict, line: List, original_header: List, path: str, format_output: str) -> str:
    annotations_header = ann[AnnotationGeneralKeys.ANNOTATION.name]
    row_parser = []
    for k, v in annotations_header.items():
        row_parser.append(AnnotationTypesParsers[v[0]].value(v, line, original_header, path))
    return AnnotationFormat[format_output.upper()].value.join(list(map(str, row_parser)))


def _parser(file: str, annotation: dict, format_output: str, display_header=True) -> Generator[str, None, None]:
    row = None
    fd = open(file, "rt")

    header = list(annotation[AnnotationGeneralKeys.ANNOTATION.name].keys())
    original_header = None
    for lnum, line in _base_parser(fd):
        if original_header is None:
            original_header = line.split()
            try:
                if not display_header:
                    continue
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


def _check_extension(ext: str, path: str) -> re.Match:
    rext = re.compile(ext[-1:] + "$")
    return rext.search(path)


def _unify(base_path: str, annotation: Annotation, display_header=True) -> Generator[str, None, None]:
    an = annotation.structure
    format_output = annotation.format
    if isfile(base_path):
        for ext, ann in an.items():
            if _check_extension(ext, base_path):
                for x in _parser(base_path, ann, format_output, display_header):
                    display_header = False
                    yield x
    else:
        try:
            for file in listdir(base_path):
                file_path = join(base_path, file)
                if isfile(file_path):
                    for ext, ann in an.items():
                        if _check_extension(ext, file_path):
                            for x in _parser(file_path, ann, format_output, display_header):
                                display_header = False
                                yield x
                else:
                    for x in _unify(file_path, annotation, display_header):
                        display_header = False
                        yield x
        except PermissionError as e:
            print(e)


class Variant:

    def __init__(self, path: str, ann: Annotation) -> None:
        self._path: str = path
        self._annotation: Annotation = ann
        self._generator: Generator[str, None, None] = _unify(path, ann)

    def read(self, display_header=True) -> Generator[str, None, None]:
        for i, line in enumerate(self._generator):
            if display_header and i == 0:
                yield line
            elif i != 0:
                yield line

    def save(self, file_path: str, display_header=True):
        if isdir(file_path):
            raise ValueError("The path must be a file.")
        with open(file_path, "w") as file:
            writer = csv.writer(file, delimiter=AnnotationFormat[self._annotation.format.upper()].value)
            for line in self.read(display_header):
                writer.writerow(line.split())
            file.close()

    '''
    def __preprocess_chunk(self, file, chunk):
        return join(dirname(file), "bgvariants", "preprocess", basename(file), "c{:06d}.bgvars.xz".format(chunk))
    '''

    def _selection_input(self):
        selection = []
        print(self._path)
        for i in find_files(self._path, self._annotation):
            print(i)
            selection += [(i, self._annotation)]
        return selection

    '''
    def count(self):
        selection = self._selection_input()
        with Pool(os.cpu_count()) as pool:
            task = functools.partial(run)
            map_method = pool.imap_unordered if len(selection) > 1 else map

            total = 0
            groups = {}
            for c, g in tqdm(
                    map_method(task, selection),
                    total=len(selection),
                    desc="Counting variants".rjust(40),
                    disable=(len(selection) < 2)
            ):
                # Update groups
                if g is not None:
                    for k, v in g.items():
                        val = groups.get(k, 0)
                        groups[k] = val + v

                total += c
        print(total)
        return total
        '''
