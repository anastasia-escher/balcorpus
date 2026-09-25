"""Tests for reading spreadsheet cells as numbers."""

from django.test import SimpleTestCase

from core.processing.importing.cleaning import clean_number


class CleanNumberTests(SimpleTestCase):
    def test_whole_numbers_are_read(self):
        self.assertEqual(clean_number('1902'), 1902)
        self.assertEqual(clean_number(1902.0), 1902)
        self.assertEqual(clean_number('0'), 0)

    def test_anything_else_is_not_a_number(self):
        self.assertIsNone(clean_number('1.5'))
        self.assertIsNone(clean_number('um 1900'))
        self.assertIsNone(clean_number(''))

    def test_a_negative_number_is_not_read(self):
        # Every column read this way is stored as a number of zero or more.
        self.assertIsNone(clean_number('-1'))
        self.assertIsNone(clean_number(-1902.0))
