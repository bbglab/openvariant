from src.annotation.annotation import Annotation
from src.utils.logger import log

from src.reader.find import find_files
from src.unify.unify import unify

if __name__ == '__main__':
    # for k, r in find_files('./test/data/example1'):
    ann = Annotation('test/data/example1/example1.yaml')
    print(ann.structure)
    for i, x in enumerate(unify('./test/data', ann.structure)):
        print(x)
