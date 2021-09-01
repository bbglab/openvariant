from src.annotation.annotation import Annotation
from src.utils.logger import log

from src.finder.find import find_files
from src.variant.variant import Variant

if __name__ == '__main__':
    # for k, r in find_files('./test/data/example1'):
    ann = Annotation('test/data/example.yaml')
    result = Variant('./test/data/example1/ACC.maf', ann)
    result.save("results.tsv")
