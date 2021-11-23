import unittest

from openvariant.utils.where import parse_where


class TestWhere(unittest.TestCase):

    def test_where(self):
        where_stmt_eq = parse_where("KEY == VALUE")
        result_eq = [{'OPERATION': 'EQUAL', 'FIELD': 'KEY', 'VALUE': 'VALUE'}]

        where_stmt_neq = parse_where("KEY != VALUE")
        result_neq = [{'OPERATION': 'NOEQUAL', 'FIELD': 'KEY', 'VALUE': 'VALUE'}]

        where_stmt_beq = parse_where("KEY >= VALUE")
        result_beq = [{'OPERATION': 'MOREEQUAL', 'FIELD': 'KEY', 'VALUE': 'VALUE'}] 
        
        where_stmt_leq = parse_where("KEY <= VALUE")
        result_leq = [{'OPERATION': 'LESSEQUAL', 'FIELD': 'KEY', 'VALUE': 'VALUE'}]

        where_stmt_b = parse_where("KEY > VALUE")
        result_b = [{'OPERATION': 'MORE', 'FIELD': 'KEY', 'VALUE': 'VALUE'}]

        where_stmt_l = parse_where("KEY < VALUE")
        result_l = [{'OPERATION': 'LESS', 'FIELD': 'KEY', 'VALUE': 'VALUE'}]

        self.assertEqual(where_stmt_eq, result_eq, 'Where statement not matching')
        self.assertEqual(where_stmt_neq, result_neq, 'Where statement not matching')
        self.assertEqual(where_stmt_beq, result_beq, 'Where statement not matching')
        self.assertEqual(where_stmt_leq, result_leq, 'Where statement not matching')
        self.assertEqual(where_stmt_b, result_b, 'Where statement not matching')
        self.assertEqual(where_stmt_l, result_l, 'Where statement not matching')

    def test_invalid_where(self):
        with self.assertRaises(ValueError):
            parse_where("KEY=VALUE")
