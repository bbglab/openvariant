import os
from enum import Enum
from functools import partial


def _add_action(name: str) -> None:
    if os.path.exists(f"{os.getcwd()}/{name}"):
        raise FileExistsError(f"Directory {os.getcwd()}/{name} already exists.")
    os.mkdir(f"{os.getcwd()}/{name}")


class PluginActions(Enum):
    ADD = partial(_add_action)
