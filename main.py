from os import getcwd

from openvariant import findfiles, Annotation, Variant

# where = "VAR != 4 AND (VAR != 5 OR VAR != 10)"
# where_clauses = parse_where(where)
# print(where_clauses)
# print(skip({"VAR": 4}, where_clauses))

# print(and_connector("VAR != 4 ", "VAR != 5"))

#res = count(f'{getcwd()}/tests/data/dataset/', f'{getcwd()}/tests/data/task_test.yaml',
#            where="DATASET != 'acc'", quite=True)
#print(res)


#annotation = Annotation(f"{getcwd()}/tests/data/dataset/dataset.yaml")

for file, ann in findfiles(f"{getcwd()}/tests/data/dataset/sample3"):
    result = Variant(file, ann)
    for line in result.read(where="REF != 'A',REF != 'G'"):
        print(f"Line in a dict: {line}")
        break
