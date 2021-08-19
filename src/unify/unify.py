from os.path import isfile

from src.unify.parser import parser


def unify(base_path: str, annotation: dict):
    if isfile(base_path):
        return parser(base_path, annotation)
    # parser(base_path, annotation)
