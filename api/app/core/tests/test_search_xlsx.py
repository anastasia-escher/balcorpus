"""Tests for downloading the whole result of a search as an Excel file."""

import io
from unittest import mock

from django.test import TestCase
from openpyxl import load_workbook

from .corpus_fixtures import make_sentence

XLSX_URL = '/api/v1/tokens/search/xlsx/'


class SearchXlsxTests(TestCase):
    def setUp(self):
        self.sentence = make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            pos_tags=['Ncfsny', 'Vapip3s-n', 'Rgp', 'Ap-fs-n', 'Z'],
            heads=[4, 4, 4, 0, 4],
            relations=['nsubj:pass', 'aux:pass', 'advmod', 'root', 'punct'],
        )

    def sheet(self, response):
        return load_workbook(io.BytesIO(response.content)).active

    def test_a_search_comes_back_as_a_file_with_one_row_per_match(self):
        response = self.client.get(XLSX_URL, {'lemma': 'убав'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        header, row = self.sheet(response).values
        self.assertEqual(header[0], 'text_id')
        self.assertEqual(
            row,
            ('panov_pechalbari_1936', 'Печалбари', 1, 'anton_panov', 'Антон Панов',
             'убаво', 'убав', 'Rgp', 'advmod', None, 'Комедијата е убаво напишана.'),
        )

    def test_text_that_looks_like_a_formula_stays_text(self):
        make_sentence(
            '=SUM(1) да',
            lemmas=['=SUM(1)', 'да'],
            text=self.sentence.text,
            speaker=self.sentence.speaker,
            sentence_id=2,
        )

        sheet = self.sheet(self.client.get(XLSX_URL, {'lemma': '=SUM(1)'}))

        source = sheet['F2']
        self.assertEqual(source.value, '=SUM(1)')
        self.assertEqual(source.data_type, 's')

    def test_a_search_without_criteria_is_refused(self):
        self.assertEqual(self.client.get(XLSX_URL).status_code, 400)

    def test_too_many_matches_are_refused(self):
        with mock.patch('core.views.MAX_EXPORT_ROWS', 0):
            response = self.client.get(XLSX_URL, {'lemma': 'убав'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('Narrow the search', response.json()['detail'])
