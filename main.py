from src.reader.find import find_files

if __name__ == '__main__':
    x = find_files('./test/data/')
    for k in x:
        print(k)
