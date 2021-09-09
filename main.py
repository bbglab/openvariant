from src.annotation.annotation import Annotation
from src.task.count import count
from src.task.find import find_files

if __name__ == '__main__':
    # for k, r in find_files('./test/data/example1'):

    annotation = Annotation('test/data/example.yaml')
    for f, ann in find_files('./test/data/', annotation):
        print(f, ann.annotations)
    print(count('./test/data', 'test/data/example.yaml', group_by='DATASET', where='PROJECT != 2', quite=True))
