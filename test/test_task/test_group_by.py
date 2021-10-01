import unittest

from src.task.groupby import group_by


class TestGroupBy(unittest.TestCase):

    # Normal group by functionality
    def test_group_by(self):
        res_expect = ['kich', 'chol', 'meso', 'laml', 'acc', 'ucs']
        res = [g for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET', quite=True))]
        self.assertEqual(res, res_expect)

    def test_invalid_group_by(self):
        res = list(group_by('./test/data/', 'test/data/task_test.yaml', 'NO_EXIST', quite=True))
        self.assertEqual(res, [])

    # Using where attribute
    def test_group_by_equal_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="DATASET == \"acc\"", quite=True)):
            res_groups.add(g)
            if g != 'acc':
                self.assertListEqual(v, [])
            else:
                self.assertNotEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_non_equal_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="DATASET != \"acc\"", quite=True)):
            res_groups.add(g)
            if g == 'acc':
                self.assertListEqual(v, [])
            else:
                self.assertNotEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_little_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="PROJECT < \"example2\"", quite=True)):
            res_groups.add(g)

            if g in ['chol', 'acc']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_leq_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="PROJECT <= \"example2\"", quite=True)):
            res_groups.add(g)

            if g in ['chol', 'acc', 'laml', 'kich']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_great_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="PROJECT > \"example2\"", quite=True)):
            res_groups.add(g)

            if g in ['meso', 'ucs']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_geq_than_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="PROJECT >= \"example2\"", quite=True)):
            res_groups.add(g)

            if g in ['meso', 'ucs', 'laml', 'kich']:
                self.assertNotEqual(v, [])
            else:
                self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_no_exist_where(self):
        res_expect_groups = {'kich', 'chol', 'meso', 'laml', 'acc', 'ucs'}
        res_groups = set()
        for g, v in list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET',
                                  where="NOT_EXIST == \"not_exist\"", quite=True)):
            res_groups.add(g)
            self.assertEqual(v, [])

        self.assertEqual(res_groups, res_expect_groups)

    def test_group_by_bad_fromat_where(self):
        with self.assertRaises(ValueError):
            list(group_by('./test/data/', 'test/data/task_test.yaml', 'DATASET', where="NOT_EXIST = \"not_exist\"",
                          quite=True))


if __name__ == '__main__':
    unittest.main()
