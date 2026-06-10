import unittest

class TestCoreImport(unittest.TestCase):
    def test_import_core(self):
        try:
            import openvariant._core
            print("Successfully imported openvariant._core")
        except ImportError as e:
            self.fail(f"Failed to import openvariant._core: {e}")

if __name__ == '__main__':
    unittest.main()
