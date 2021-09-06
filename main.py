import functools
import os
from multiprocessing import Pool

from tqdm import tqdm

from src.annotation.annotation import Annotation
from src.task.count import count

from src.task.find import find_files

if __name__ == '__main__':
    # for k, r in find_files('./test/data/example1'):
    count('test/data/example.yaml', './test/data/')

# for x in result.read():
#    print(x)
