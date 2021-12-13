import unittest
from os import getcwd

from click.testing import CliRunner

from openvariant.task.openvar import count


class TestCountCommand(unittest.TestCase):

    def test_count_command(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(result.output, None)

    def test_count_command_more_flags(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--group_by', 'DATASET',
                                       '--where', "variant == 'DEL'",
                                       '--annotations', f'{getcwd()}/tests/data/example1/example1.yaml',
                                       '--cores', '2', '--quite'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(result.output, None)

    def test_count_no_exist_command_input(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/no_exist'])

        self.assertTrue(f"Error: Invalid value for '[INPUT_PATH]': Path '{getcwd()}/tests/data/no_exist' does not exist."
                        in result.output)
        self.assertEqual(result.exit_code, 2)

    def test_count_command_no_exist_group_by(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--group_by', 'NO_EXIST', '-q'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'TOTAL\t0\n')

    def test_count_command_invalid_group_by(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--group_by'])

        self.assertEqual(result.exit_code, 2)

    def test_count_command_no_exist_where_flag(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--where', "variant='no_exist'"])

        self.assertEqual(result.exit_code, 1)

    def test_count_command_invalid_where_flag(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--where'])

        self.assertEqual(result.exit_code, 2)

    def test_count_command_no_exist_annotation(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--annotations',
                                       f'{getcwd()}/tests/data/example1/no_exist.yaml'])

        self.assertTrue(f"Error: Invalid value for '--annotations' / '-a': Path "
                        f"'{getcwd()}/tests/data/example1/no_exist.yaml' does not exist."
                        in result.output)
        self.assertEqual(result.exit_code, 2)

    def test_count_command_invalid_annotation(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--annotations'])

        self.assertEqual(result.exit_code, 2)

    def test_count_command_no_exist_cores(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--cores', 'NO_EXIST'])

        self.assertEqual(result.exit_code, 2)

    def test_count_command_invalid_cores(self):
        runner = CliRunner()
        result = runner.invoke(count, [f'{getcwd()}/tests/data/example1', '--cores'])

        self.assertEqual(result.exit_code, 2)

    def test_count_command_no_args(self):
        runner = CliRunner()
        result = runner.invoke(count, [])

        self.assertEqual(result.exit_code, 1)
