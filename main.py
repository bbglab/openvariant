from src.annotation.annotation import Annotation
from src.task.count import count
from src.task.find import find_files
from src.variant.variant import Variant

if __name__ == '__main__':
    annotation = Annotation('test/data/example.yaml')

    result = Variant('./test/data/example1', annotation)
    result.save('res.tsv')
    #for x in result.read():
    #    print(x)
    #    pass

    #for f, ann in find_files('./test/data/example1', annotation):
    #    print(f, ann.annotations)

    #print(count('./test/data/example1/', 'test/data/example.yaml', quite=True))
