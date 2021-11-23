import unittest
from os import getcwd

from click.testing import CliRunner

from openvariant.task.openvar import cat


class TestCatCommand(unittest.TestCase):

    def test_cat_command(self):
        runner = CliRunner()
        result = runner.invoke(cat, [f'{getcwd()}/test/data/example1', '--header'])
        self.assertEqual(result.exit_code, 0, 'Not a correct exit code')

