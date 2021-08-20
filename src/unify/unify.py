from os.path import isfile, isdir

from src.unify.parser import parser


def unify(base_path: str, annotation: dict):
    if isfile(base_path):
        return parser(base_path, annotation)

    if isdir(base_path):
        print('hee')
    # parser(base_path, annotation)
