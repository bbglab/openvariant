import unittest

from openvariant.annotation.builder import AnnotationTypesBuilders, Builder
from openvariant.config.config_annotation import AnnotationTypes, AnnotationKeys


class TestBuilder(unittest.TestCase):

    def test_builder_static(self):
        static_dict = {'type': 'static', 'field': 'PLATFORM', 'value': 'WSG'}

        res_expect = (AnnotationTypes.STATIC.name, 'WSG')
        result = AnnotationTypesBuilders[AnnotationTypes.STATIC.name].value(static_dict)

        self.assertEqual(result, res_expect)

    def test_builder_no_exist_static(self):
        with self.assertRaises(KeyError):
            static_dict = {}
            AnnotationTypesBuilders[AnnotationTypes.STATIC.name].value(static_dict)

    def test_builder_none_static(self):
        static_dict = {'type': 'static', 'field': None, 'value': None}

        res_expect = (AnnotationTypes.STATIC.name, None)
        result = AnnotationTypesBuilders[AnnotationTypes.STATIC.name].value(static_dict)

        self.assertEqual(result, res_expect)

   # def test_builder_internal(self):
   #     internal_dict = {'type': 'internal', 'field': 'variant', 'fieldSource': ['Variant_Type', 'Data']}

   #     res_expect = (AnnotationTypes.INTERNAL.value, 'WSG')
   #     type_annot, field_sources, annot, value = AnnotationTypesBuilders[AnnotationTypes.INTERNAL.name].value(
   #         internal_dict)

   #     self.assertEqual(type_annot, AnnotationTypes.INTERNAL.name)
   #     self.assertEqual(field_sources, ['Variant_Type', 'Data'])
   #     self.assertIsInstance(annot, Builder)
   #     self.assertEqual(value, float('nan'))
