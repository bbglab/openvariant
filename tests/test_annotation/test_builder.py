import math
import os
import re
import unittest
from types import MethodType

from openvariant.annotation.builder import STATIC, INTERNAL, FILENAME, DIRNAME, MAPPING, PLUGIN, Builder
from openvariant.annotation.config_annotation import AnnotationTypes
from openvariant.plugins.context import Context


class TestBuilder(unittest.TestCase):

    def test_builder_static(self):
        static_dict = {'type': 'static', 'field': 'PLATFORM', 'value': 'WSG'}

        res_expect = (AnnotationTypes.STATIC.name, 'WSG')

        instance = STATIC()
        result = instance(static_dict)

        self.assertEqual(result, res_expect)

    def test_builder_no_exist_static(self):
        with self.assertRaises(KeyError):
            static_dict = {'type': 'static'}
            instance = STATIC()
            instance(static_dict)

    def test_builder_none_static(self):
        static_dict = {'type': 'static', 'field': None, 'value': None}

        res_expect = (AnnotationTypes.STATIC.name, None)

        instance = STATIC()
        result = instance(static_dict)

        self.assertEqual(result, res_expect)

    def test_builder_internal(self):
        internal_dict = {'type': 'internal', 'field': 'variant', 'fieldSource': ['Variant_Type', 'Data'],
                         'function': "lambda c: c.upper().replace('CHR', '').replace('23', 'X').replace('24', 'Y')"}

        instance = INTERNAL()
        type_annot, field_sources, annot, value = instance(internal_dict)

        self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
        self.assertEqual(field_sources, ['Variant_Type', 'Data'])
        self.assertIsInstance(annot, Builder)
        self.assertIsNone(value)

    def test_builder_internal_with_value(self):
        internal_dict = {'type': 'internal', 'field': 'sample', 'fieldSource': ['icgc_sample_id', 'icgc_specimen_id'],
                         'value': '{icgc_sample_id}_{icgc_specimen_id}'}

        instance = INTERNAL()
        type_annot, field_sources, annot, value = instance(internal_dict)

        self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
        self.assertEqual(field_sources, ['icgc_sample_id', 'icgc_specimen_id'])
        self.assertIsInstance(annot, Builder)
        self.assertEqual(value, '{icgc_sample_id}_{icgc_specimen_id}')

    def test_builder_invalid_internal(self):
        internal_dict = {'type': 'internal', 'field': 'variant', 'fieldSource': None, 'function': None}

        instance = INTERNAL()
        type_annot, field_sources, annot, value = instance(internal_dict)

        self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
        self.assertEqual(field_sources, None)
        self.assertIsInstance(annot, Builder)

    def test_builder_invalid_internal_with_value(self):
        internal_dict = {'type': 'internal', 'field': 'sample', 'fieldSource': ['icgc_sample_id', 'icgc_specimen_id'],
                         'value': None}

        instance = INTERNAL()
        type_annot, field_sources, annot, value = instance(internal_dict)

        self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
        self.assertEqual(field_sources, ['icgc_sample_id', 'icgc_specimen_id'])
        self.assertIsInstance(annot, Builder)
        self.assertEqual(value, None)

    def test_builder_no_exist_internal(self):
        internal_dict = {'type': 'internal'}

        with self.assertRaises(KeyError):
            instance = INTERNAL()
            instance(internal_dict)

    def test_builder_dirname(self):
        dirname_dict = {'type': 'dirname', 'field': 'PROJECT', 'function': 'lambda x: "{}".format(x.lower()[:-4])',
                        'regex': '[a-zA-Z0-9]*.'}

        instance = DIRNAME()
        type_annot, annot, regexp = instance(dirname_dict)

        self.assertEqual(type_annot, AnnotationTypes.DIRNAME.name)
        self.assertIsInstance(annot, Builder)
        self.assertIsInstance(regexp, re.Pattern)

    def test_builder_invalid_dirname(self):
        dirname_dict = {'type': 'dirname', 'field': 'PROJECT', 'function': None,
                        'regex': None}
        instance = DIRNAME()
        type_annot, annot, regexp = instance(dirname_dict)

        self.assertEqual(type_annot, AnnotationTypes.DIRNAME.name)
        self.assertIsInstance(annot, Builder)
        self.assertIsInstance(regexp, re.Pattern)

    def test_builder_invalid_regex_dirname(self):
        dirname_dict = {'type': 'dirname', 'field': 'PROJECT', 'function': None,
                        'regex': ']['}

        with self.assertRaises(re.error):
            instance = DIRNAME()
            instance(dirname_dict)

    def test_builder_filename(self):
        filename_dict = {'type': 'filename', 'field': 'DATASET', 'function': 'lambda x: "{}".format(x.lower()[:-4])',
                         'regex': '[a-zA-Z0-9]*.'}

        instance = FILENAME()
        type_annot, annot, regexp = instance(filename_dict)

        self.assertEqual(type_annot, AnnotationTypes.FILENAME.name)
        self.assertIsInstance(annot, Builder)
        self.assertIsInstance(regexp, re.Pattern)

    def test_builder_invalid_filename(self):
        filename_dict = {'type': 'filename', 'field': 'DATASET', 'function': None,
                         'regex': None}

        instance = FILENAME()
        type_annot, annot, regexp = instance(filename_dict)

        self.assertEqual(type_annot, AnnotationTypes.FILENAME.name)
        self.assertIsInstance(annot, Builder)
        self.assertIsInstance(regexp, re.Pattern)

    def test_builder_invalid_regex_filename(self):
        filename_dict = {'type': 'filename', 'field': 'DATASET', 'function': None,
                         'regex': ']['}

        with self.assertRaises(re.error):
            instance = FILENAME()
            instance(filename_dict)

    def test_builder_mapping(self):
        mapping_dict = {'type': 'mapping', 'field': 'CANCER_TYPE', 'fieldSource': ['donor_id', 'id', 'Donor_Id'],
                        'fieldMapping': 'icgc_donor_id', 'fileMapping': 'metadata.tsv', 'fieldValue': 'cancer_type'}
        annotation_path = f'{os.getcwd()}/tests/data/builder/metadata.yaml'

        expect_mapping = {'DO48316': 'ESCA', 'DO48318': 'ESCA', 'DO48312': 'ESCA', 'DO50633': 'EWS'}

        instance = MAPPING()
        type_annot, field_sources, mapping = instance(mapping_dict, annotation_path)

        self.assertEqual(type_annot, AnnotationTypes.MAPPING.name)
        self.assertEqual(field_sources, ['donor_id', 'id', 'Donor_Id'])
        self.assertEqual(mapping, expect_mapping)

    def test_builder_invalid_mapping(self):
        mapping_dict = {'type': 'mapping', 'field': 'CANCER_TYPE', 'fieldSource': None,
                        'fieldMapping': None, 'fileMapping': None, 'fieldValue': None}
        annotation_path = f'{os.getcwd()}/tests/data/builder/metadata.yaml'

        with self.assertRaises(FileNotFoundError):
            instance = MAPPING()
            instance(mapping_dict, annotation_path)

    def test_builder_invalid_file_mapping(self):
        mapping_dict = {'type': 'mapping', 'field': 'CANCER_TYPE', 'fieldSource': ['donor_id', 'id', 'Donor_Id'],
                        'fieldMapping': 'icgc_donor_id', 'fileMapping': 'no_exist.tsv', 'fieldValue': 'cancer_type'}
        annotation_path = f'{os.getcwd()}/tests/data/builder/metadata.yaml'

        with self.assertRaises(FileNotFoundError):
            instance = MAPPING()
            instance(mapping_dict, annotation_path)

    def test_builder_invalid_path_mapping(self):
        mapping_dict = {'type': 'mapping', 'field': 'CANCER_TYPE', 'fieldSource': ['donor_id', 'id', 'Donor_Id'],
                        'fieldMapping': 'icgc_donor_id', 'fileMapping': 'metadata.tsv', 'fieldValue': 'cancer_type'}
        annotation_path = None

        with self.assertRaises(TypeError):
            instance = MAPPING()
            instance(mapping_dict, annotation_path)

    def test_builder_plugin(self):
        plugin_dict = {'type': 'plugin', 'plugin': 'alteration_type', 'field': 'ALT_TYPE'}

        instance =  PLUGIN()
        type_annot, func, ctxt = instance(plugin_dict)

        self.assertEqual(type_annot, AnnotationTypes.PLUGIN.name)
        self.assertIsInstance(func, MethodType)
        self.assertTrue(issubclass(ctxt, Context))

    def test_builder_invalid_plugin(self):
        os.environ['OPENVAR_PLUGIN'] = '/test/to/plugin/'

        plugin_dict = {'type': 'plugin', 'plugin': None, 'field': None}

        with self.assertRaises(FileNotFoundError):
            instance = PLUGIN()
            instance(plugin_dict)
