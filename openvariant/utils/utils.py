import re
import os
from appdirs import user_data_dir
from fnmatch import fnmatch
from os.path import basename
import importlib


ENV_VAR = {
    'OPENVAR_PLUGIN': user_data_dir('openvariant', 'bbglab')
}


def loadEnvironmentVariables() -> None:
    """Load environment variable into the environment."""

    missing_vars = set(ENV_VAR.keys()).difference(set(os.environ))

    for env_var in missing_vars:
        os.environ[env_var] = ENV_VAR[env_var]
        os.makedirs(ENV_VAR[env_var], exist_ok=True)

    return


def check_extension(ext: str, path: str) -> bool:
    """Check if file matches with the annotation pattern"""
    return fnmatch(basename(path), ext) if ext[0] == '*' else re.match(ext, basename(path)) is not None


def import_class_from_module(module_name, class_name):
    """Import annotation class"""
    try:
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_        
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error: {e}")
        return None
