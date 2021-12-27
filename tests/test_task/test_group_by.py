import os
import unittest

from openvariant.commands.tasks.groupby import group_by


class TestGroupBy(unittest.TestCase):

    def test_group_by_basic(self):
        res_expect = {'chol', 'kich', 'meso', 'laml', 'acc', 'ucs'}
        res = set(
            [g for g, _, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/',
                                            f'{os.getcwd()}/tests/data/task_test.yaml',
                                            None, key_by='DATASET', quite=True))])

        self.assertEqual(res, res_expect)

    def test_invalid_group_by(self):
        res = list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                            None, key_by='NO_EXIST', quite=True))

        self.assertEqual(res, [])

    def test_group_by_equal_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/',
                                     f'{os.getcwd()}/tests/data/task_test.yaml', None,
                                     key_by='DATASET', where="DATASET == \"acc\"", quite=True)):

            res_groups.add(g)
            if g != 'acc':
                self.assertListEqual(v, [])
            else:
                self.assertNotEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_non_equal_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                                     None, 'DATASET', where="DATASET != \"acc\"", quite=True)):

            res_groups.add(g)
            if g == 'acc':
                self.assertListEqual(v, [])
            else:
                self.assertNotEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_little_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                                     None, key_by='DATASET', where="PROJECT < \"SAMPLE1\"", quite=True)):

            res_groups.add(g)
            if g in ['chol', 'acc']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_leq_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                                     None, 'DATASET', where="PROJECT <= \"SAMPLE1\"", quite=True)):
            res_groups.add(g)

            if g in ['chol', 'acc', 'meso', 'ucs']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_great_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                                     None, 'DATASET', where="PROJECT > \"SAMPLE1\"", quite=True)):

            res_groups.add(g)
            if g in ['laml', 'kich']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_geq_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml', None,
                                     'DATASET', where="PROJECT >= \"SAMPLE1\"", quite=True)):
            res_groups.add(g)
            if g in ['meso', 'ucs', 'laml', 'kich']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_no_exist_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v, _ in list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml',
                                     None, 'DATASET', where="NOT_EXIST == \"not_exist\"", quite=True)):
            res_groups.add(g)
            self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_bad_format_where(self):
        with self.assertRaises(ValueError):
            list(group_by(f'{os.getcwd()}/tests/data/dataset/', f'{os.getcwd()}/tests/data/task_test.yaml', None,
                          'DATASET', where="NOT_EXIST = \"not_exist\"", quite=True))
