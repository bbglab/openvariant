from src.reader.find import find_files

if __name__ == '__main__':
    for k, r in find_files('./test/data/'):
        print(k, r)
