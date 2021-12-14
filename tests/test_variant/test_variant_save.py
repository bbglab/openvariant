import os
import unittest

from openvariant.annotation.annotation import Annotation
from openvariant.variant.variant import Variant


class TestVariantSave(unittest.TestCase):

    def test_variant_save(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/example1', annotation)

        variant.save(f'{os.getcwd()}/tests/data/variant/save.tsv')

    def test_variant_save_invalid_path(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/example1', annotation)

        with self.assertRaises(ValueError):
            variant.save(f'{os.getcwd()}/tests/data/variant/')

    def test_variant_save_invalid_None(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/example1', annotation)

        with self.assertRaises(ValueError):
            variant.save(None)
