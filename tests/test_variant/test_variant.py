import os
import unittest

from openvariant.annotation.annotation import Annotation
from openvariant.variant.variant import Variant


class TestVariant(unittest.TestCase):

    def test_variant_creation(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/example1', annotation)

        self.assertNotEqual(variant, None)

    def test_variant_invalid_annotation(self):
        with self.assertRaises(ValueError):
            Variant(f'{os.getcwd()}/tests/data/example1', None)

    def test_variant_invalid_path(self):
        with self.assertRaises(ValueError):
            annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
            Variant(None, annotation)

    def test_variant_path(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        path = f'{os.getcwd()}/tests/data/example1'
        variant = Variant(path, annotation)

        self.assertEqual(variant.path, path)

    def test_variant_header(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        res_expected = {'PLATFORM', 'variant', 'DATASET', 'PROJECT'}
        variant = Variant(f'{os.getcwd()}/tests/data/example1', annotation)

        self.assertEqual(set(variant.header), res_expected)

    def test_variant_annotation(self):
        annotation = Annotation(f'{os.getcwd()}/tests/data/example1/example1.yaml')
        variant = Variant(f'{os.getcwd()}/tests/data/example1', annotation)

        self.assertEqual(variant.annotation, annotation)

