from src.annotation.annotation import Annotation
from src.task.cat import cat
from src.task.count import count
from src.task.find import find_files
from src.task.groupby import sub_group_by, group_by
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

    print(count('./test/data/example1/', 'test/data/example.yaml', where="A == 99955985", quite=True))
    #cat('./test/data/example1/', 'test/data/example.yaml', where="A != \"acc\"")

    #x = list(sub_group_by('./test/data/example1', annotation, "A"))
    #print(x[0])
    #print(group_by(x))