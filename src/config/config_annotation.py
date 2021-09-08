from enum import Enum

ANNOTATION_EXTENSION = "yaml"
DEFAULT_FORMAT = 'TSV'
DEFAULT_RECURSIVE = False


class AnnotationGeneralKeys(Enum):
    PATTERN = 'pattern'
    RECURSIVE = 'recursive'
    FORMAT = 'format'
    ANNOTATION = 'annotation'
    EXCLUDES = 'excludes'


class AnnotationKeys(Enum):
    TYPE = 'type'
    FIELD = 'field'
    VALUE = 'value'
    FIELD_SOURCE = 'fieldSource'
    FUNCTION = 'function'
    COORDINATE_SOURCE = 'coordinateSource'
    COORDINATE_TARGET = 'coordinateTarget'
    MAPPING_FILE = 'mappingFile'
    MAPPING_FIELD = 'mappingField'


class ExcludesKeys(Enum):
    FIELD = 'field'
    VALUE = 'value'


class AnnotationTypes(Enum):
    STATIC = 'static'
    INTERNAL = 'internal'
    DIRNAME = 'dirname'
    FILENAME = 'filename'
    LIFTOVER = 'liftover'
    MAPPING = 'mapping'


class AnnotationFormat(Enum):
    TSV = "\t"
    CSV = ","
