import os
import tempfile
import unittest

from openvariant.tasks.plugin import CREATE


class TestPluginTask(unittest.TestCase):

    def test_create_uses_pascal_case_class_names(self):
        previous_plugin_path = os.environ.get('OPENVAR_PLUGIN')

        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['OPENVAR_PLUGIN'] = tmpdir
            try:
                CREATE()('add_date')
            finally:
                if previous_plugin_path is None:
                    os.environ.pop('OPENVAR_PLUGIN', None)
                else:
                    os.environ['OPENVAR_PLUGIN'] = previous_plugin_path

            with open(f'{tmpdir}/add_date/add_date.py') as plugin_file:
                plugin_content = plugin_file.read()

        self.assertIn('class AddDateContext(Context):', plugin_content)
        self.assertIn('class AddDatePlugin(Plugin):', plugin_content)
        self.assertIn('run(context: AddDateContext)', plugin_content)
        self.assertIn('def run(self, context: AddDateContext) -> dict:', plugin_content)
        self.assertNotIn('Add_date', plugin_content)
