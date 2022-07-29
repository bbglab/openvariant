import pkg_resources

from openvariant.annotation.annotation import Annotation
from openvariant.tasks import cat, count, group_by
from openvariant.variant import Variant
from openvariant.find_files import findfiles

version = pkg_resources.require("open-variant")[0].version
__version__ = version

__all__ = ['Annotation', 'Variant', 'cat', 'count', 'group_by', 'findfiles']

