import unittest
from os import getcwd

from click.testing import CliRunner

from openvariant.task.openvar import cat


class TestCatCommand(unittest.TestCase):

    def test_cat_command(self):
        runner = CliRunner()
        result = runner.invoke(cat, [f'{getcwd()}/tests/data/example1'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(result.output, None)

    def test_cat_command_more_flags(self):
        runner = CliRunner()
        result = runner.invoke(cat, [f'{getcwd()}/tests/data/example1', '--header', '--where', "variant == 'DEL'",
                                     '--annotations', f'{getcwd()}/tests/data/example1/example1.yaml'])

        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(result.output, None)

    def test_cat_path_no_exist_command(self):
        runner = CliRunner()
        result = runner.invoke(cat, [f'{getcwd()}/tests/data/no_exist'], catch_exceptions=False)

        self.assertTrue(f"Error: Invalid value for '[INPUT_PATH]': Path '{getcwd()}/tests/data/no_exist' does not exist."
                        in result.output)
        self.assertEqual(result.exit_code, 2)

    def test_cat_path_command_invalid_flags(self):
        runner = CliRunner()
        result = runner.invoke(cat, [f'{getcwd()}/tests/data/example1', '--where', "variant='no_exist'"])
        self.assertEqual(result.exit_code, 1)

    def test_cat_command_invalid_annotation(self):
        runner = CliRunner()
        result = runner.invoke(cat, [f'{getcwd()}/tests/data/example1', '--annotations',
                                     f'{getcwd()}/tests/data/example1/no_exist.yaml'])
        self.assertEqual(result.exit_code, 1)
