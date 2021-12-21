import os
import unittest
from typing import List

from openvariant.find.find import find_files


class TestFind(unittest.TestCase):

    def test_find_files(self):
        f_expect = {f'{os.getcwd()}/tests/data/dataset/sample2/KICH.maf',
                    f'{os.getcwd()}/tests/data/dataset/sample2/LAML.maf',
                    f'{os.getcwd()}/tests/data/dataset/sample1/MESO.maf',
                    f'{os.getcwd()}/tests/data/dataset/sample1/UCS.maf',
                    f'{os.getcwd()}/tests/data/dataset/sample3/data_mutations_extended.txt',
                    f'{os.getcwd()}/tests/data/dataset/ACC.maf',
                    f'{os.getcwd()}/tests/data/dataset/CHOL.maf'}

        res_list = find_files(f'{os.getcwd()}/tests/data/dataset')
        f_res, a_res = zip(*list(res_list))

        self.assertEqual(set(f_res), f_expect)
        self.assertIsInstance(list(a_res), List)

    def test_with_annotation_find_files(self):
        res_expect = {f'{os.getcwd()}/tests/data/dataset/sample2/KICH.maf',
                      f'{os.getcwd()}/tests/data/dataset/sample2/LAML.maf',
                      f'{os.getcwd()}/tests/data/dataset/sample1/MESO.maf',
                      f'{os.getcwd()}/tests/data/dataset/sample1/UCS.maf',
                      f'{os.getcwd()}/tests/data/dataset/ACC.maf',
                      f'{os.getcwd()}/tests/data/dataset/CHOL.maf'}

        res = set(
            [f for f, a in list(find_files(f'{os.getcwd()}/tests/data/dataset',
                                           f'{os.getcwd()}/tests/data/dataset/dataset.yaml'))])
        self.assertEqual(res, res_expect)

    def test_no_exist_find_files(self):
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files(f'{os.getcwd()}/tests/data/dataset/no-exist',
                                               f'{os.getcwd()}/tests/data/dataset/dataset.yaml'))])

    def test_no_exist_annotation_find_files(self):
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files(f'{os.getcwd()}/tests/data/dataset',
                                               f'{os.getcwd()}/tests/data/dataset/no_exist.yaml'))])

    def test_invalid_annotation_find_files(self):
        with self.assertRaises(FileNotFoundError):
            set([f for f, a in list(find_files(f'{os.getcwd()}/tests/data/dataset',
                                               f'{os.getcwd()}/tests/data/dataset/no_exist.yaml'))])
