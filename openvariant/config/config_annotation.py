from enum import Enum

ANNOTATION_EXTENSION = "yaml"
DEFAULT_FORMAT = 'TSV'
DEFAULT_COLUMNS = []
DEFAULT_RECURSIVE = False
DEFAULT_DELIMITER = 'T'


class AnnotationGeneralKeys(Enum):
    PATTERN = 'pattern'
    RECURSIVE = 'recursive'
    FORMAT = 'format'
    DELIMITER = 'delimiter'
    COLUMNS = 'columns'
    ANNOTATION = 'annotation'
    EXCLUDE = 'exclude'


class AnnotationKeys(Enum):
    TYPE = 'type'
    FIELD = 'field'
    PLUGIN = 'plugin'
    VALUE = 'value'
    FIELD_SOURCE = 'fieldSource'
    FUNCTION = 'function'
    REGEX = 'regex'
    FILE_MAPPING = 'fileMapping'
    FIELD_MAPPING = 'fieldMapping'
    FIELD_VALUE = 'fieldValue'


class ExcludesKeys(Enum):
    FIELD = 'field'
    VALUE = 'value'


class AnnotationTypes(Enum):
    STATIC = 'static'
    INTERNAL = 'internal'
    DIRNAME = 'dirname'
    FILENAME = 'filename'
    PLUGIN = 'plugin'
    MAPPING = 'mapping'


class AnnotationDelimiter(Enum):
    T = "\t"
    C = ","


class AnnotationFormat(Enum):
    TSV = "\t"
    CSV = ","
