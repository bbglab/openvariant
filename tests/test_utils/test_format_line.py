import unittest

from openvariant.utils.format_line import format_line


class TestFormatLine(unittest.TestCase):

    def test_format_line_tsv(self):
        text = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'Praesent', 'bibendum']
        text_output = format_line(text, 'tsv')
        response = 'Lorem\tipsum\tdolor\tsit\tamet\tconsectetur\tadipiscing\telit\tPraesent\tbibendum'
        self.assertEqual(text_output, response, "Formatting text not matching")

    def test_format_line_csv(self):
        text = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'Praesent', 'bibendum']
        text_output = format_line(text, 'csv')
        response = 'Lorem,ipsum,dolor,sit,amet,consectetur,adipiscing,elit,Praesent,bibendum'
        self.assertEqual(text_output, response, "Formatting text not matching")

    def test_empty_format_line(self):
        text = []
        text_output = format_line(text, 'tsv')
        response = ''
        self.assertEqual(text_output, response, "Formatting text not matching")

    def test_invalid_format_line(self):
        with self.assertRaises(KeyError):
            text = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'Praesent', 'bibendum']
            format_line(text, 'no_exist')
