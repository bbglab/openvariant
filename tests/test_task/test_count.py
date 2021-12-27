import os
import unittest

from openvariant.commands.tasks.count import count


class TestCount(unittest.TestCase):

    def test_count_basic(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml', quite=True)

        self.assertEqual(res[0], 42130, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_invalid_count(self):
        with self.assertRaises(FileNotFoundError):
            count(f'{os.getcwd()}/tests/data/dataset/no-exist', f'{os.getcwd()}/tests/data/no-exist.yaml',
                  quite=True)

    def test_count_equal_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="DATASET == \"acc\"", quite=True)

        self.assertEqual(res[0], 11660, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_non_equal_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="DATASET != \"acc\"", quite=True)

        self.assertEqual(res[0], 30470, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_little_than_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="POSITION < 52366244", quite=True)

        self.assertEqual(res[0], 17734, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_leq_than_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="POSITION <= 52366244", quite=True)

        self.assertEqual(res[0], 17735, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_great_than_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="POSITION > 52366244", quite=True)

        self.assertEqual(res[0], 24395, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_geq_than_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="POSITION >= 52366244", quite=True)

        self.assertEqual(res[0], 24396, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_no_exist_where(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    where="NO_EXIST == \"no_exist\"", quite=True)

        self.assertEqual(res[0], 0, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_bad_syntax_where(self):
        with self.assertRaises(ValueError):
            count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                  where="NO_EXIST = \"no_exist\"", quite=True)

    def test_count_group_by(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    group_by="DATASET", quite=True)

        self.assertEqual(res[0], 42130, "Count number not matching")
        self.assertEqual(res[1], {'kich': 3268, 'chol': 4500, 'meso': 3980, 'laml': 8313, 'acc': 11660, 'ucs': 10409},
                         "Count groups not matching")

    def test_count_invalid_group_by(self):
        res = count(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                    group_by="NO_EXIST", quite=True)

        self.assertEqual(res[0], 0, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")
