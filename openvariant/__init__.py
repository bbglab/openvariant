from multiprocessing import set_start_method

from openvariant.annotation.annotation import Annotation
from openvariant.tasks import cat, count, group_by
from openvariant.variant import Variant
from openvariant.find_files import findfiles

try:
    from importlib.metadata import version  # Python 3.8+
except ImportError:
    from importlib_metadata import version  # Backport for older versions

__version__ = version("open-variant")

# Set multiprocessing start method to 'spawn'
try:
    set_start_method('spawn', force=True)
except RuntimeError:
    pass

__all__ = ['Annotation', 'Variant', 'cat', 'count', 'group_by', 'findfiles']

