import unittest

from src.task.count import count


class TestCount(unittest.TestCase):

    # Normal count functionality
    def test_count(self):
        res = count('./test/data/', 'test/data/task_test.yaml', quite=True)
        self.assertEqual(res[0], 42130, "Count number not matching")

    # Using where attribute
    def test_count_equal_where(self):
        pass

    def test_count_non_equal_where(self):
        pass

    def test_count_little_than_where(self):
        pass

    def test_count_leq_than_where(self):
        pass

    def test_count_great_than_where(self):
        pass

    def test_count_geq_than_where(self):
        pass

    def test_count_invalid_where(self):
        pass

    # Using group by attribute
    def test_count_group_by(self):
        pass

    def test_count_invalid_group_by(self):
        pass


if __name__ == '__main__':
    unittest.main()
