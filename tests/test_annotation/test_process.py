import math
import re
import unittest
from types import MethodType

from openvariant.annotation.builder import StaticBuilder, InternalBuilder, Builder, DirnameBuilder, FilenameBuilder, \
    PluginBuilder, MappingBuilder
from openvariant.annotation.process import AnnotationTypesProcess, InternalProcess, DirnameProcess, FilenameProcess
from openvariant.config.config_annotation import AnnotationTypes
from openvariant.plugins.context import Context


def _func_plugin_example(line):
    return 'Hello World'


class TestProcess(unittest.TestCase):

    def test_process_static(self):
        static_dict: StaticBuilder = (AnnotationTypes.STATIC.name, 'WSG')

        res_expect = (AnnotationTypes.STATIC.name, 'WSG', str)
        result = AnnotationTypesProcess[AnnotationTypes.STATIC.name].value(static_dict)

        self.assertEqual(result, res_expect)

    def test_process_no_exist_static(self):
        with self.assertRaises(TypeError):
            static_dict: StaticBuilder = None
            AnnotationTypesProcess[AnnotationTypes.STATIC.name].value(static_dict)

    def test_process_none_static(self):
        static_dict: StaticBuilder = (AnnotationTypes.STATIC.name, None)

        result = AnnotationTypesProcess[AnnotationTypes.STATIC.name].value(static_dict)

        self.assertTrue(math.isnan(result[1]))

    def test_process_internal(self):
        internal_dict: InternalBuilder = (AnnotationTypes.INTERNAL.name, ['POS', 'Data'],
                                          Builder("(lambda y: y)"), None)
        original_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT']

        type_annot, value, func = AnnotationTypesProcess[AnnotationTypes.INTERNAL.name].value(internal_dict,
                                                                                              original_header)

        self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
        self.assertEqual(value, 1)
        self.assertIsInstance(func, Builder)

    def test_process_invalid_internal(self):
        internal_dict: InternalBuilder = (AnnotationTypes.INTERNAL.name, ['Data'],
                                          Builder("(lambda y: y)"), None)

        original_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT']

        type_annot, value, func = AnnotationTypesProcess[AnnotationTypes.INTERNAL.name].value(
            internal_dict, original_header)

        self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
        self.assertEqual(value, None)
        self.assertIsInstance(func, Builder)

    def test_process_no_exist_internal(self):
        with self.assertRaises(TypeError):
            internal_dict: InternalBuilder = (AnnotationTypes.INTERNAL.name, None,
                                              Builder("(lambda y: y)"), None)
            original_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT']

            AnnotationTypesProcess[AnnotationTypes.INTERNAL.name].value(internal_dict, original_header)

    def test_process_dirname(self):
        dirname_dict: DirnameBuilder = (AnnotationTypes.DIRNAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))

        res_expect = (AnnotationTypes.DIRNAME.name, 'dirname', str)

        result = AnnotationTypesProcess[AnnotationTypes.DIRNAME.name].value(dirname_dict, [], '/dirname/filename.tsv')

        self.assertEqual(result, res_expect)

    def test_process_invalid_path_dirname(self):
        dirname_dict: DirnameBuilder = (AnnotationTypes.DIRNAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))

        with self.assertRaises(TypeError):
            AnnotationTypesProcess[AnnotationTypes.FILENAME.name].value(dirname_dict, [], None)

    def test_process_invalid_regex_dirname(self):
        dirname_dict: DirnameBuilder = (AnnotationTypes.DIRNAME.name, Builder("(lambda y: y)"), None)

        with self.assertRaises(AttributeError):
            AnnotationTypesProcess[AnnotationTypes.FILENAME.name].value(dirname_dict, [], '/dirname/filename.tsv')

    def test_process_filename(self):
        filename_dict: FilenameBuilder = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))

        res_expect = (AnnotationTypes.FILENAME.name, 'filename.tsv', str)

        result = AnnotationTypesProcess[AnnotationTypes.FILENAME.name].value(filename_dict, [], '/dirname/filename.tsv')

        self.assertEqual(result, res_expect)

    def test_process_invalid_path_filename(self):
        filename_dict: FilenameBuilder = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))

        with self.assertRaises(TypeError):
            AnnotationTypesProcess[AnnotationTypes.FILENAME.name].value(filename_dict, [], None)

    def test_process_invalid_regex_filename(self):
        filename_dict: FilenameBuilder = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), None)

        with self.assertRaises(AttributeError):
            AnnotationTypesProcess[AnnotationTypes.FILENAME.name].value(filename_dict, [], '/dirname/filename.tsv')

    def test_process_mapping(self):
        mapping_dict: MappingBuilder = (AnnotationTypes.MAPPING.name, ['PROPERTY'], {'CANCER': 'BLCA'})
        head_schema = {'PROPERTY': ('MAPPING', 'CANCER', str)}

        res_expect = (AnnotationTypes.MAPPING.name, ('MAPPING', ['PROPERTY'], {'CANCER': 'BLCA'}), str)

        result = AnnotationTypesProcess[AnnotationTypes.MAPPING.name].value(mapping_dict, [], None, head_schema)

        self.assertEqual(result, res_expect)

    #def test_process_invalid_mapping(self):
    #    mapping_dict: MappingBuilder = (AnnotationTypes.MAPPING.name, None, None)
    #    head_schema = {'PROPERTY': ('MAPPING', 'CANCER', str)}

    #    with self.assertRaises(ValueError):
    #        AnnotationTypesProcess[AnnotationTypes.MAPPING.name].value(mapping_dict, [], None, head_schema)

    #def test_process_invalid_head_schema_mapping(self):
    #    mapping_dict: MappingBuilder = (AnnotationTypes.MAPPING.name, ['PROPERTY'], {'CANCER': 'BLCA'})
    #    head_schema = {}

    #    with self.assertRaises(KeyError):
    #        AnnotationTypesProcess[AnnotationTypes.MAPPING.name].value(mapping_dict, [], None, head_schema)

    def test_process_plugin(self):
        plugin_dict: PluginBuilder = (AnnotationTypes.PLUGIN.name, _func_plugin_example,
                                      Context({'FIELD_EXAMPLE': None}, 'FIELD_EXAMPLE', '/workspace/file.tsv'))

        res_expect = (AnnotationTypes.PLUGIN.name, plugin_dict[2], plugin_dict[1])

        result = AnnotationTypesProcess[AnnotationTypes.PLUGIN.name].value(plugin_dict)

        self.assertEqual(result, res_expect)

    def test_process_invalid_plugin(self):
        plugin_dict: PluginBuilder = (AnnotationTypes.PLUGIN.name, None)

        with self.assertRaises(ValueError):
            AnnotationTypesProcess[AnnotationTypes.PLUGIN.name].value(plugin_dict)
