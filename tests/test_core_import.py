import importlib
import unittest


class TestCoreImport(unittest.TestCase):
    def test_import_core(self):
        importlib.import_module('openvariant._core')
