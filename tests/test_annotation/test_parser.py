import os
import re
import unittest

from openvariant.annotation.builder import Builder
from openvariant.annotation.parser import AnnotationTypesParsers
from openvariant.config.config_annotation import AnnotationTypes


def function_plugin(x: dict) -> dict:
    del x['CHROMOSOME']
    return x


def invalid_function_plugin(x: dict) -> dict:
    del x['INVALID']
    return x


class TestParser(unittest.TestCase):

    def test_parser_static(self):
        static_tuple = (AnnotationTypes.STATIC.name, 'WSG')
        res_expected = 'WSG'

        result = AnnotationTypesParsers[AnnotationTypes.STATIC.name].value(static_tuple)

        self.assertEqual(result, res_expected)

    def test_parser_num_static(self):
        static_tuple = (AnnotationTypes.STATIC.name, 1234)
        res_expected = '1234'

        result = AnnotationTypesParsers[AnnotationTypes.STATIC.name].value(static_tuple)

        self.assertEqual(result, res_expected)

    def test_parser_invalid_static(self):
        static_tuple = (AnnotationTypes.STATIC.name, None)
        res_expected = 'nan'

        result = AnnotationTypesParsers[AnnotationTypes.STATIC.name].value(static_tuple)

        self.assertEqual(result, res_expected)

    def test_parser_internal(self):
        internal_tuple = (
            AnnotationTypes.INTERNAL.name, ['NCBI_Build', 'Center'], Builder("(lambda y: y)"), float('nan'))
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']
        res_expected = 'GRCh37'

        result = AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line, original_header)

        self.assertEqual(result, res_expected)

    def test_parser_internal_with_value(self):
        internal_tuple = (AnnotationTypes.INTERNAL.name, [['icgc_sample_id', 'icgc_specimen_id']],
                          Builder("(lambda y: y)"), '{icgc_sample_id}_{icgc_specimen_id}')
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['icgc_sample_id', 'icgc_specimen_id', 'Center', 'NCBI_Build', 'Chromosome']
        res_expected = 'CARD6_0'

        result = AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line, original_header)

        self.assertEqual(result, res_expected)

    def test_parser_internal_invalid_builder(self):
        internal_tuple = (AnnotationTypes.INTERNAL.name, None, None, None)
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']

        with self.assertRaises(TypeError):
            AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line, original_header)

    def test_parser_internal_invalid_field_sources(self):
        internal_tuple = (AnnotationTypes.INTERNAL.name, ['X'], Builder("(lambda y: y)"), float('nan'))
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']
        res_expected = str(float('nan'))

        result = AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line, original_header)

        self.assertEqual(result, res_expected)

    def test_parser_internal_invalid_function(self):
        internal_tuple = (AnnotationTypes.INTERNAL.name, ['NCBI_Build', 'Center'], Builder("(lambday:y)"), float('nan'))
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']

        with self.assertRaises(SyntaxError):
            AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line, original_header)

    def test_parser_internal_invalid_value(self):
        internal_tuple = (AnnotationTypes.INTERNAL.name, [['icgc_sample_id', 'icgc_specimen_id']],
                          Builder("(lambda y: y)"), '{icgc_sample_id}_{icgc_specimen_id}')
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['X', 'Y', 'Center', 'NCBI_Build', 'Chromosome']
        res_expected = f"{str(float('nan'))}_{str(float('nan'))}"

        result = AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line, original_header)

        self.assertEqual(result, res_expected)

    def test_parser_internal_invalid_parameters(self):
        internal_tuple = (
            AnnotationTypes.INTERNAL.name, ['NCBI_Build', 'Center'], Builder("(lambda y: y)"), float('nan'))

        with self.assertRaises(TypeError):
            AnnotationTypesParsers[AnnotationTypes.INTERNAL.name].value(internal_tuple, line=None,
                                                                        original_header=None)

    def test_parser_filename(self):
        filename_tuple = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))
        path = f'{os.getcwd()}/tests/data/example.maf'
        res_expected = 'example.maf'

        result = AnnotationTypesParsers[AnnotationTypes.FILENAME.name].value(filename_tuple, path=path)

        self.assertEqual(result, res_expected)

    def test_parser_filename_invalid_path(self):
        filename_tuple = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))
        path = f'{os.getcwd()}/tests/data/'

        with self.assertRaises(FileNotFoundError):
            AnnotationTypesParsers[AnnotationTypes.FILENAME.name].value(filename_tuple, path=path)

    def test_parser_filename_no_exist_path(self):
        filename_tuple = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))
        path = None

        with self.assertRaises(TypeError):
            AnnotationTypesParsers[AnnotationTypes.FILENAME.name].value(filename_tuple, path=path)

    def test_parser_filename_invalid_function(self):
        filename_tuple = (AnnotationTypes.FILENAME.name, Builder("(lambday:y)"), re.compile('(.*)'))
        path = f'{os.getcwd()}/tests/data/example.maf'

        with self.assertRaises(SyntaxError):
            AnnotationTypesParsers[AnnotationTypes.FILENAME.name].value(filename_tuple, path=path)

    def test_parser_filename_invalid_regex(self):
        filename_tuple = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile("[][]"))
        path = f'{os.getcwd()}/tests/data/example.maf'

        with self.assertRaises(re.error):
            AnnotationTypesParsers[AnnotationTypes.FILENAME.name].value(filename_tuple, path=path)

    def test_parser_dirname(self):
        dirname_tuple = (AnnotationTypes.DIRNAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))
        path = f'{os.getcwd()}/tests/data/example.maf'
        res_expected = 'data'

        result = AnnotationTypesParsers[AnnotationTypes.DIRNAME.name].value(dirname_tuple, path=path)

        self.assertEqual(result, res_expected)

    def test_parser_dirname_invalid_path(self):
        dirname_tuple = (AnnotationTypes.FILENAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))
        path = f'{os.getcwd()}/tests/data/'

        with self.assertRaises(FileNotFoundError):
            AnnotationTypesParsers[AnnotationTypes.DIRNAME.name].value(dirname_tuple, path=path)

    def test_parser_dirname_no_exist_path(self):
        dirname_tuple = (AnnotationTypes.DIRNAME.name, Builder("(lambda y: y)"), re.compile('(.*)'))
        path = None

        with self.assertRaises(TypeError):
            AnnotationTypesParsers[AnnotationTypes.DIRNAME.name].value(dirname_tuple, path=path)

    def test_parser_dirname_invalid_function(self):
        dirname_tuple = (AnnotationTypes.DIRNAME.name, Builder("(lambday:y)"), re.compile('(.*)'))
        path = f'{os.getcwd()}/tests/data/example.maf'

        with self.assertRaises(SyntaxError):
            AnnotationTypesParsers[AnnotationTypes.DIRNAME.name].value(dirname_tuple, path=path)

    def test_parser_dirname_invalid_regex(self):
        dirname_tuple = (AnnotationTypes.DIRNAME.name, Builder("(lambda y: y)"), re.compile("[][]"))
        path = f'{os.getcwd()}/tests/data/example.maf'

        with self.assertRaises(re.error):
            AnnotationTypesParsers[AnnotationTypes.DIRNAME.name].value(dirname_tuple, path=path)

    def test_parser_plugin(self):
        plugin_tuple = (AnnotationTypes.PLUGIN.name, [], function_plugin)
        dict_line = {'CHROMOSOME': '1', 'POSITION': '123551001', 'STRAND': '+', 'REF': 'A'}
        result = AnnotationTypesParsers[AnnotationTypes.PLUGIN.name].value(plugin_tuple, dict_line=dict_line)
        res_expected = {'POSITION': '123551001', 'STRAND': '+', 'REF': 'A'}

        self.assertEqual(result, res_expected)

    def test_parser_invalid_dict_plugin(self):
        plugin_tuple = (AnnotationTypes.PLUGIN.name, [], function_plugin)

        with self.assertRaises(Exception):
            AnnotationTypesParsers[AnnotationTypes.PLUGIN.name].value(plugin_tuple, dict_line=None)

    def test_parser_no_exist_func_plugin(self):
        plugin_tuple = (AnnotationTypes.PLUGIN.name, [], None)
        dict_line = {'CHROMOSOME': '1', 'POSITION': '123551001', 'STRAND': '+', 'REF': 'A'}
        with self.assertRaises(KeyError):
            AnnotationTypesParsers[AnnotationTypes.PLUGIN.name].value(plugin_tuple, dict_line=dict_line)

    def test_parser_invalid_func_plugin(self):
        plugin_tuple = (AnnotationTypes.PLUGIN.name, [], invalid_function_plugin)
        dict_line = {'CHROMOSOME': '1', 'POSITION': '123551001', 'STRAND': '+', 'REF': 'A'}
        with self.assertRaises(Exception):
            AnnotationTypesParsers[AnnotationTypes.PLUGIN.name].value(plugin_tuple, dict_line=dict_line)

    def test_parser_mapping(self):
        mapping_tuple = (AnnotationTypes.MAPPING.name, ['SETNAME'], {'a8eb251b': 'C3L-04475-02',
                                                                     'dba745f4': 'C3L-01598-02',
                                                                     'f3812e87': 'C3N-01388-03'})
        dict_line = {'CHROMOSOME': '1', 'SETNAME': 'f3812e87', 'STRAND': '+', 'REF': 'A'}
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']
        result = AnnotationTypesParsers[AnnotationTypes.MAPPING.name].value(mapping_tuple, line=line,
                                                                            original_header=original_header,
                                                                            dict_line=dict_line)
        res_expected = 'C3N-01388-03'

        self.assertEqual(result, res_expected)

    def test_parser_mapping_empty_fields(self):
        mapping_tuple = (AnnotationTypes.MAPPING.name, [], {'a8eb251b': 'C3L-04475-02',
                                                            'dba745f4': 'C3L-01598-02',
                                                            'f3812e87': 'C3N-01388-03'})
        dict_line = {'CHROMOSOME': '1', 'SETNAME': 'f3812e87', 'STRAND': '+', 'REF': 'A'}
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']
        result = AnnotationTypesParsers[AnnotationTypes.MAPPING.name].value(mapping_tuple, line=line,
                                                                            original_header=original_header,
                                                                            dict_line=dict_line)

        self.assertEqual(result, 'nan')

    def test_parser_mapping_empty_map(self):
        mapping_tuple = (AnnotationTypes.MAPPING.name, ['SETNAME'], {})
        dict_line = {'CHROMOSOME': '1', 'SETNAME': 'f3812e87', 'STRAND': '+', 'REF': 'A'}
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']
        result = AnnotationTypesParsers[AnnotationTypes.MAPPING.name].value(mapping_tuple, line=line,
                                                                            original_header=original_header,
                                                                            dict_line=dict_line)

        self.assertEqual(result, 'nan')

    def test_parser_no_exist_mapping(self):
        mapping_tuple = (AnnotationTypes.MAPPING.name, None, None)
        dict_line = {'CHROMOSOME': '1', 'SETNAME': 'f3812e87', 'STRAND': '+', 'REF': 'A'}
        line = ['CARD6', '0', '.', 'GRCh37', '5', '40841514']
        original_header = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build', 'Chromosome']

        with self.assertRaises(ValueError):
            AnnotationTypesParsers[AnnotationTypes.MAPPING.name].value(mapping_tuple, line=line,
                                                                       original_header=original_header,
                                                                       dict_line=dict_line)

    def test_parser_invalid_parameters_mapping(self):
        mapping_tuple = (AnnotationTypes.MAPPING.name, ['SETNAME'], {'a8eb251b': 'C3L-04475-02',
                                                                     'dba745f4': 'C3L-01598-02',
                                                                     'f3812e87': 'C3N-01388-03'})

        with self.assertRaises(ValueError):
            AnnotationTypesParsers[AnnotationTypes.MAPPING.name].value(mapping_tuple, line=None, original_header=None,
                                                                       dict_line=None)
