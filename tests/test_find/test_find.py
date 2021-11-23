import os
import unittest
from typing import List

from openvariant.find.find import find_files


class TestFind(unittest.TestCase):

    def test_find_files(self):
        f_expect = {f'{os.getcwd()}/tests/data/example2/KICH.maf', f'{os.getcwd()}/tests/data/example2/LAML.maf',
                    f'{os.getcwd()}/tests/data/example1/ACC.maf', f'{os.getcwd()}/tests/data/example1/CHOL.maf',
                    f'{os.getcwd()}/tests/data/example3/MESO.maf', f'{os.getcwd()}/tests/data/example3/UCS.maf'}

        res_list = find_files(f'{os.getcwd()}/tests/data')
        f_res, a_res = zip(*list(res_list))

        self.assertEqual(set(f_res), f_expect)
        self.assertIsInstance(list(a_res), List)

    def test_with_annotation_find_files(self):
        res_expect = {f'{os.getcwd()}/tests/data/example2/KICH.maf', f'{os.getcwd()}/tests/data/example2/LAML.maf',
                      f'{os.getcwd()}/tests/data/example1/ACC.maf', f'{os.getcwd()}/tests/data/example1/CHOL.maf',
                      f'{os.getcwd()}/tests/data/example3/MESO.maf', f'{os.getcwd()}/tests/data/example3/UCS.maf'}

        res = set(
            [f for f, a in list(find_files(f'{os.getcwd()}/tests/data', f'{os.getcwd()}/tests/data/example.yaml'))])
        self.assertEqual(res, res_expect)

    def test_invalid_find_files(self):
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files(f'{os.getcwd()}/tests/data/no-exist',
                                               f'{os.getcwd()}/tests/data/example.yaml'))])

    def test_invalid_annotation_find_files(self):
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files(f'{os.getcwd()}/tests/data/',
                                               f'{os.getcwd()}/tests/data/no_exist.yaml'))])
