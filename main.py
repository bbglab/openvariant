import os
from os import getcwd

from openvariant.annotation.annotation import Annotation
from openvariant.task.count import count
from openvariant.task.groupby import group_by
from openvariant.variant.variant import Variant

for g, v, _ in group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
         None, key_by='DATASET', where="PROJECT >= \"SAMPLE1\"", quite=True):
    print(g, len(v))
