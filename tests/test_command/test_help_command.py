import unittest

from click.testing import CliRunner

from openvariant.commands.openvar import main


class TestHelpCommand(unittest.TestCase):

    def test_help_command(self):
        runner = CliRunner()
        result = runner.invoke(main)
        self.assertTrue("cat      Concatenate files to standard input" in result.output)
        self.assertTrue("count    Number of rows that matches a specified criterion" in result.output)
        self.assertTrue("groupby  Groups rows that have the same values into summary rows" in result.output)
