from os import getcwd

from openvariant import find_files, Annotation, Variant

# where = "VAR != 4 AND (VAR != 5 OR VAR != 10)"
# where_clauses = parse_where(where)
# print(where_clauses)
# print(skip({"VAR": 4}, where_clauses))

# print(and_connector("VAR != 4 ", "VAR != 5"))

#res = count(f'{getcwd()}/tests/data/dataset/', f'{getcwd()}/tests/data/task_test.yaml',
#            where="DATASET != 'acc'", quite=True)
#print(res)


annotation = Annotation(f"{getcwd()}/tests/data/dataset/dataset.yaml")

#for file, _ in find_files(f"{getcwd()}/tests/data/dataset/"):

result = Variant(f"{getcwd()}/tests/data/dataset/sample3/", annotation)
for line in result.read():
    print(f"Line in a dict: {line}")
    break
