from src.reader.find import find_files
from src.unify.unify import unify

if __name__ == '__main__':
    for k, r in find_files('./test/data/example1'):
        print(k, r)

        for i, x in enumerate(unify(k, r)):
            if i == 0:
                print(x)
            print(x)
