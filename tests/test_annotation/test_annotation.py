import unittest
from os import getcwd

from openvariant.annotation.annotation import Annotation
from openvariant.config.config_annotation import DEFAULT_FORMAT, DEFAULT_DELIMITER


class TestAnnotation(unittest.TestCase):

    def test_annotation_creation(self):
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertNotEqual(annotation, None)

    def test_annotation_invalid_creation(self):
        with self.assertRaises(FileNotFoundError):
            Annotation(f'{getcwd()}/tests/data/no_exist.yaml')

    def test_annotation_patterns(self):
        res_expect = {'*.maf', '*.vcf.gz'}
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertEqual(set(annotation.patterns), res_expect)

    def test_annotation_invalid_patterns(self):
        with self.assertRaises(TypeError):
            Annotation(f'{getcwd()}/tests/data/annotation/invalid_pattern.yaml')

    def test_annotation_no_exist_patterns(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/no_exist_pattern.yaml')

    def test_annotation_format(self):
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertEqual(annotation.format, 'CSV')

    def test_annotation_no_exist_format(self):
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/no_exist_format.yaml')
        self.assertEqual(annotation.format, DEFAULT_FORMAT)

    def test_annotation_invalid_format(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/invalid_format.yaml')

    def test_annotation_delimiter(self):
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertEqual(annotation.delimiter, 'C')

    def test_annotation_no_exist_delimiter(self):
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/no_exist_delimiter.yaml')
        self.assertEqual(annotation.delimiter, DEFAULT_DELIMITER)

    def test_annotation_invalid_delimiter(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/invalid_delimiter.yaml')

    def test_annotation_columns(self):
        res_expect = {'PLATFORM', 'DATASET'}
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertEqual(set(annotation.columns), res_expect)

    def test_annotation_no_exist_columns(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/no_exist_columns.yaml')

    def test_annotation_invalid_columns(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/invalid_columns.yaml')

    def test_annotation_annotations(self):
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertNotEqual(annotation.annotations, None)

    def test_annotation__no_exist_annotations(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/no_exist_annotation.yaml')

    def test_annotation_excludes(self):
        res_expect = [{'field': 'MUTATION_REF', 'value': 1234}, {'field': 'DATASET', 'value': 'ucs'}]
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        self.assertEqual(annotation.excludes, res_expect)

    def test_annotation_no_exist_excludes(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/no_exist_excludes.yaml')

    def test_annotation_invalid_excludes(self):
        with self.assertRaises(KeyError):
            Annotation(f'{getcwd()}/tests/data/annotation/invalid_excludes.yaml')

    def test_annotation_structure(self):
        res_expect = {'*.maf', '*.vcf.gz'}
        annotation = Annotation(f'{getcwd()}/tests/data/annotation/annotation.yaml')
        result_pattern = set(annotation.structure.keys())
        result_structure = annotation.structure.values()

        self.assertEqual(result_pattern, res_expect)
        self.assertNotEqual(result_structure, None)
