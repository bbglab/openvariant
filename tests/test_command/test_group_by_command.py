import unittest
from os import getcwd

from click.testing import CliRunner

from openvariant.commands.openvar import groupby


class TestGroupByCommand(unittest.TestCase):

    def test_group_by_command(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(result.output, None)

    def test_group_by_command_more_flags(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--header', '--show', '--group_by',
                                         'DATASET', '--where', "variant == 'DEL'", '--script', 'wc -l',
                                         '--annotations', f'{getcwd()}/tests/data/dataset/dataset.yaml',
                                         '--cores', '2', '--quite'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(result.output, None)

    def test_group_by_no_exist_command_input(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/no_exist'])

        self.assertTrue(
            f"Error: Invalid value for '[INPUT_PATH]': Path '{getcwd()}/tests/data/no_exist' does not exist."
            in result.output)
        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_no_exist_group_by(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by', 'NO_EXIST'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '')

    def test_group_by_command_invalid_group_by(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by'])

        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_no_exist_where(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by',
                                         'DATASET', '--where', "variant='no_exist'"])

        self.assertEqual(result.exit_code, 1)

    def test_group_by_command_invalid_where(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by',
                                         'DATASET', '--where'])

        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_invalid_script(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by',
                                         'DATASET', '--script'])

        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_no_exist_annotation(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by',
                                         'DATASET', '--annotations', f'{getcwd()}/tests/data/dataset/no_exist.yaml'])

        self.assertTrue(f"Error: Invalid value for '--annotations' / '-a': Path "
                        f"'{getcwd()}/tests/data/dataset/no_exist.yaml' does not exist."
                        in result.output)
        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_invalid_annotation(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by', 'DATASET', '--annotations'])

        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_no_exist_cores(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by', 'DATASET',
                                         '--cores', 'NO_EXIST'])

        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_invalid_cores(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [f'{getcwd()}/tests/data/dataset', '--group_by', 'DATASET', '--cores'])

        self.assertEqual(result.exit_code, 2)

    def test_group_by_command_no_args(self):
        runner = CliRunner()
        result = runner.invoke(groupby, [])

        self.assertEqual(result.exit_code, 1)
