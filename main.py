import os

from openvariant.commands.tasks.groupby import group_by

for g, v, _ in group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
         None, key_by='DATASET', where="PROJECT >= \"SAMPLE1\"", quite=True):
    print(g, len(v))
