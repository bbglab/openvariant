from src.annotation.annotation import Annotation
from src.task.cat import cat
from src.task.count import count
from src.task.find import find_files
from src.task.groupby import group_by
from src.variant.variant import Variant

if __name__ == '__main__':
    #annotation = Annotation('test/data/example_X.yaml')
    #print(annotation.annotations)

    #result = Variant('./test/data/', annotation)
    #for r in result.read():
    #    print(r)

    #print(count('./test/data/', 'test/data/task_test.yaml', where="DATASET == \"acc\"", quite=True))

    #result = Variant('./test/data/', annotation)
    #for r in result.read():
    #    a, dataset, project = (r["A"], r["DATASET"], r["PROJECT"])
    #    print(a, "-", dataset, "-", project)

    #result = Variant('./test/data/example1', annotation)
    #for x in result.read():
        #print(x)
        #print(x['A'])
    #    pass

    #for f, ann in find_files('./test/data/example1', annotation):
    #    print(f, ann.excludes)

    #print([f for f,a in list(find_files('./test/data/grr', annotation))])
    #print(count('./test/data/', 'test/data/example_X.yaml', quite=True))
    #for f, a in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET', where="NOT_EXIST = \"not_exist\"", quite=True)):
    #    print(f, not len(a) == 0)
    #print(count('./tes-t/data/', 'test/data/count_test.yaml', where="DATASET != \"acc\"", quite=True))
    #print(count('./test/data/example1/', 'test/data/example.yaml', quite=True))
    #cat('./test/data/example1/', 'test/data/example.yaml', where="A != \"acc\"")

    for key, group in group_by('./test/data/', './test/data/example.yaml', "PROJECT", quite=True):
        print(key, len(group))
    #print(group_by(x))

