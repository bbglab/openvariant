import unittest

from src.task.count import count


class TestCount(unittest.TestCase):

    # Count functionality
    def test_count(self):
        res = count('./test/data/', 'test/data/task_test.yaml', quite=True)
        self.assertEqual(res[0], 42130, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_invalid_count(self):
        with self.assertRaises(FileNotFoundError):
            res = count('test/data/no-exist', 'test/data/no-exist.yaml', quite=True)

    # Using where attribute
    def test_count_equal_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="DATASET == \"acc\"", quite=True)
        self.assertEqual(res[0], 11660, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_non_equal_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="DATASET != \"acc\"", quite=True)
        self.assertEqual(res[0], 30470, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_little_than_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="A < 52366244", quite=True)
        self.assertEqual(res[0], 17734, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_leq_than_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="A <= 52366244", quite=True)
        self.assertEqual(res[0], 17735, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_great_than_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="A > 52366244", quite=True)
        self.assertEqual(res[0], 24395, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_geq_than_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="A >= 52366244", quite=True)
        self.assertEqual(res[0], 24396, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_no_exist_where(self):
        res = count('./test/data/', 'test/data/task_test.yaml', where="NO_EXIST == \"no_exist\"", quite=True)
        self.assertEqual(res[0], 0, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")

    def test_count_bad_syntax_where(self):
        with self.assertRaises(ValueError):
            count('./test/data/', 'test/data/task_test.yaml', where="NO_EXIST = \"no_exist\"", quite=True)

    # Using group by attribute
    def test_count_group_by(self):
        res = count('./test/data/', 'test/data/task_test.yaml', group_by="DATASET", quite=True)
        self.assertEqual(res[0], 42130, "Count number not matching")
        self.assertEqual(res[1], {'kich': 3268, 'chol': 4500, 'meso': 3980, 'laml': 8313, 'acc': 11660, 'ucs': 10409},
                         "Count groups not matching")

    def test_count_invalid_group_by(self):
        res = count('./test/data/', 'test/data/task_test.yaml', group_by="NO_EXIST", quite=True)
        self.assertEqual(res[0], 0, "Count number not matching")
        self.assertEqual(res[1], {}, "Count groups not matching")


if __name__ == '__main__':
    unittest.main()
