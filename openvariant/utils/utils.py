import re
import os
from appdirs import user_data_dir
from fnmatch import fnmatch
from os.path import basename


ENV_VAR = {
    'OPENVAR_PLUGIN': user_data_dir('openvariant', 'bbglab')
    }

def loadEnvironmentVariables():
    """Load environment variable into the environment."""

    missing_vars = set(ENV_VAR.keys()).difference(set(os.environ))

    for env_var in missing_vars:
        os.environ[env_var] = ENV_VAR[env_var]
        os.makedirs(ENV_VAR[env_var], exist_ok=True)

    return

def check_extension(ext: str, path: str) -> bool:
    """Check if file matches with the annotation pattern"""
    return fnmatch(basename(path), ext) if ext[0] == '*' else re.match(ext, basename(path)) is not None
