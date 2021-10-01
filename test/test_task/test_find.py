import unittest
from os import getcwd

from src.annotation.annotation import Annotation
from src.task.find import find_files


class TestFind(unittest.TestCase):

    def test_find_files(self):
        res_expect = {'test/data/example2/KICH.maf', 'test/data/example2/LAML.maf', 'test/data/example1/ACC.maf',
                      'test/data/example1/CHOL.maf', 'test/data/example3/MESO.maf', 'test/data/example3/UCS.maf'}

        annotation = Annotation('test/data/example.yaml')
        res = set([f for f, a in list(find_files('test/data', annotation))])
        self.assertEqual(res, res_expect)

    def test_invalid_find_files(self):
        annotation = Annotation('test/data/example.yaml')
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files('test/data/no-exist', annotation))])


if __name__ == '__main__':
    unittest.main()
