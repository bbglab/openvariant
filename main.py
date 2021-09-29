from src.annotation.annotation import Annotation
from src.task.cat import cat
from src.task.count import count
from src.task.find import find_files
from src.task.groupby import group_by
from src.variant.variant import Variant

if __name__ == '__main__':
    annotation = Annotation('test/data/example.yaml')

    #result = Variant('./test/data/example1', annotation)
    #for x in result.read():
        #print(x)
        #print(x['A'])
    #    pass

    #for f, ann in find_files('./test/data/example1', annotation):
    #    print(f, ann.excludes)

    print([f for f,a in list(find_files('./test/data/grr', annotation))])
    #print(count('./test/data/', 'test/data/count_test.yaml', where="DATASET != \"acc\"", quite=True))
    #print(count('./test/data/example1/', 'test/data/example.yaml', quite=True))
    #cat('./test/data/example1/', 'test/data/example.yaml', where="A != \"acc\"")

    #for key, group in group_by('./test/data/example1', annotation, "DATASET"):
    #    print(key, group)
    #print(group_by(x))