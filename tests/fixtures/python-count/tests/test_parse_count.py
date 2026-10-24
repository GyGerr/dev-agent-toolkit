import unittest

from parse_count import parse_count


class ParseCountTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(parse_count("0"), 0)

    def test_positive(self):
        self.assertEqual(parse_count("12"), 12)
