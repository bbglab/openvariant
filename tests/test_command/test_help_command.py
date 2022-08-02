import unittest

from click.testing import CliRunner

from openvariant.commands.openvar import openvar


class TestHelpCommand(unittest.TestCase):

    def test_help_command(self):
        runner = CliRunner()
        result = runner.invoke(openvar)
        self.assertTrue("cat      Concatenate parsed files to standard output" in result.output)
        self.assertTrue("count    Number of rows that matches a specified criterion" in result.output)
        self.assertTrue("groupby  Group the parsed result for each different value of the specified" in result.output)
        self.assertTrue("plugin   Actions to execute for a plugin: create" in result.output)
