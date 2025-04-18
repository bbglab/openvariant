import os
import unittest
import json

from openvariant.annotation.annotation import Annotation
from openvariant.variant.variant import Variant


class TestVariantRead(unittest.TestCase):

    def test_variant_read_x(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/dataset/dataset.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/dataset/CHOL.maf', annotation)

        self.assertNotEqual(variant.read(), None)

        with open(f'{os.getcwd()}/tests/data/variant/read.json') as f:
            data = json.load(f)
        for i, line in enumerate(variant.read()):
            self.assertEqual(line, data[i])

    def test_variant_read_by_key(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/dataset/dataset.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/dataset/CHOL.maf', annotation)

        self.assertNotEqual(variant.read(group_key='DATASET'), None)

        with open(f'{os.getcwd()}/tests/data/variant/read_by_key.json') as f:
            data = json.load(f)
        for i, line in enumerate(variant.read(group_key='DATASET')):
            self.assertEqual(line, data[i])
