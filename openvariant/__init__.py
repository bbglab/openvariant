import pkg_resources
version = pkg_resources.require("open-variant")[0].version
__version__ = version

