"""Tests for downloading the whole result of a search as a CSV file."""

import csv
import io
from unittest import mock

from django.test import TestCase

from .corpus_fixtures import make_sentence

CSV_URL = '/api/v1/tokens/search/csv/'


class SearchCsvTests(TestCase):
    def setUp(self):
        make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            pos_tags=['Ncfsny', 'Vapip3s-n', 'Rgp', 'Ap-fs-n', 'Z'],
            heads=[4, 4, 4, 0, 4],
            relations=['nsubj:pass', 'aux:pass', 'advmod', 'root', 'punct'],
        )

    def rows(self, response):
        text = response.content.decode('utf-8-sig')
        return list(csv.reader(io.StringIO(text)))

    def test_a_search_comes_back_as_a_file_with_one_row_per_match(self):
        response = self.client.get(CSV_URL, {'lemma': 'убав'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        header, row = self.rows(response)
        self.assertEqual(header[0], 'text_name')
        self.assertEqual(
            row,
            ['Печалбари', '1', 'Антон Панов', 'убаво', 'убав', 'Rgp', 'advmod', '',
             'Комедијата е убаво напишана.'],
        )

    def test_the_file_starts_with_a_byte_order_mark_for_excel(self):
        response = self.client.get(CSV_URL, {'lemma': 'убав'})

        self.assertTrue(response.content.startswith('﻿'.encode('utf-8')))

    def test_a_search_without_criteria_is_refused(self):
        self.assertEqual(self.client.get(CSV_URL).status_code, 400)

    def test_too_many_matches_are_refused(self):
        with mock.patch('core.views.MAX_CSV_ROWS', 0):
            response = self.client.get(CSV_URL, {'lemma': 'убав'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('Narrow the search', response.json()['detail'])
