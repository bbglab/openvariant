import unittest
from os import getcwd

from openvariant.annotation.annotation import Annotation
from openvariant.task.find import find_files


class TestFind(unittest.TestCase):

    def test_find_files(self):
        res_expect = {'tests/data/example2/KICH.maf', 'tests/data/example2/LAML.maf', 'tests/data/example1/ACC.maf',
                      'tests/data/example1/CHOL.maf', 'tests/data/example3/MESO.maf', 'tests/data/example3/UCS.maf'}

        annotation = Annotation('tests/data/example.yaml')
        res = set([f for f, a in list(find_files('tests/data', annotation))])
        self.assertEqual(res, res_expect)

    def test_invalid_find_files(self):
        annotation = Annotation('tests/data/example.yaml')
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files('tests/data/no-exist', annotation))])


if __name__ == '__main__':
    unittest.main()
