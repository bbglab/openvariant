import os
import sys
import unittest
from io import StringIO

from openvariant.commands.tasks.cat import cat


class TestCat(unittest.TestCase):

    def test_cat_basic(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset')
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_basic.tsv') as f:
            lines = f.readlines()
        self.assertEqual(captured_output.getvalue(), ''.join(lines))

    def test_cat_basic_no_valid(self):
        with self.assertRaises(TypeError):
            cat(None)

    def test_cat_with_annotation(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', f'{os.getcwd()}/tests/data/dataset/dataset.yaml')
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_with_annotation.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_equal_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="variant == 'DEL'")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_equal_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_non_equal_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="variant != 'DEL'")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_non_equal_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_less_than_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="POSITION < 56515295")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_less_than_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_leq_than_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="POSITION <= 56515295")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_leq_than_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_great_than_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="POSITION > 56515295")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_great_than_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_geq_than_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="POSITION >= 56515295")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_geq_than_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_no_exist_where(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', where="NO_EXIST == 'no_exist'")
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_no_exist_where.tsv') as f:
            lines = f.readlines()
        self.assertEqual(''.join(lines), captured_output.getvalue())

    def test_cat_invalid_where(self):
        with self.assertRaises(ValueError):
            cat(f'{os.getcwd()}/tests/data/dataset', where="NO_EXIST = 'no_exist'")

    def test_cat_no_headers(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        cat(f'{os.getcwd()}/tests/data/dataset', header_show=False)
        sys.stdout = sys.__stdout__
        with open(f'{os.getcwd()}/tests/data/task_cat/test_no_headers.tsv') as f:
            lines = f.readlines()
        self.assertEqual(captured_output.getvalue(), ''.join(lines))
