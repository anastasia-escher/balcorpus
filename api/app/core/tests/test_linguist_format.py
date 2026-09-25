"""Tests for importing an annotation file exactly as the linguists send it."""

import tempfile
from pathlib import Path

from django.test import TestCase
from openpyxl import Workbook

from core.models import Sentence, Token
from core.processing.importing.problems import DataProblems
from core.processing.importing.tokens import import_tokens

from .corpus_fixtures import make_speaker, make_text

# The heading of a linguists' file, with the trailing space the real one has.
LINGUIST_COLUMNS = [
    'sent_id', 'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos', 'pos_tag',
    'pos_ext', 'ud_valency', 'ud_type', 'speaker ', 'time', 'text_id',
]

# The byte order mark that opens some of their files, read as a word.
BYTE_ORDER_MARK_ROW = [1, 1, '﻿', None, '﻿', 'NUM', 'I', '_', 0, 'root', 'Антон Панов', None, 'Печалбари']

SENTENCE_ROWS = [
    [2, 1, 'Антон', None, 'Антон', 'PROPN', 'Npmsnn', '_', 0, 'root', 'Антон Панов', None, 'Печалбари'],
    [2, 2, 'Панов', None, 'Панов', 'PROPN', 'Npmsnn', '_', 1, 'flat', 'Антон Панов', None, 'Печалбари'],
]


class LinguistFileTests(TestCase):
    def setUp(self):
        make_text()
        make_speaker()
        self.folder = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.folder.cleanup()

    def write_file(self, rows):
        """Save the rows under the linguists' heading, with a blank row between sentences."""
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(LINGUIST_COLUMNS)
        for row in rows:
            sheet.append(row)
            sheet.append([])

        path = Path(self.folder.name) / 'pecalbari_processed_FINAL.xlsx'
        workbook.save(path)
        return path

    def test_the_file_is_imported_as_it_was_sent(self):
        summaries, _warnings = import_tokens(self.write_file([BYTE_ORDER_MARK_ROW] + SENTENCE_ROWS))

        self.assertEqual(summaries[0]['text_id'], 'panov_pechalbari_1936')
        self.assertEqual(summaries[0]['tokens'], 2)

        sentence = Sentence.objects.get()
        self.assertEqual(sentence.sentence_id, 2)
        self.assertEqual(sentence.speaker.speaker_id, 'anton_panov')
        self.assertEqual(Token.objects.get(source='Панов').head_ud_id, 1)

    def test_the_byte_order_mark_row_is_left_out_and_mentioned(self):
        _summaries, warnings = import_tokens(self.write_file([BYTE_ORDER_MARK_ROW] + SENTENCE_ROWS))

        self.assertFalse(Token.objects.filter(ud_pos='NUM').exists())
        self.assertTrue(any('no word form and no lemma' in warning for warning in warnings))

    def test_a_title_two_texts_share_needs_the_text_named(self):
        make_text(text_id='panov_pechalbari_1950', title='Печалбари')

        with self.assertRaises(DataProblems) as raised:
            import_tokens(self.write_file(SENTENCE_ROWS))

        self.assertIn('panov_pechalbari_1950', raised.exception.errors[0])

    def test_the_text_given_on_the_command_line_wins(self):
        make_text(text_id='panov_pechalbari_1950', title='Печалбари')

        summaries, _warnings = import_tokens(
            self.write_file(SENTENCE_ROWS), text_id='panov_pechalbari_1950'
        )

        self.assertEqual(summaries[0]['text_id'], 'panov_pechalbari_1950')

    def test_an_unknown_title_is_reported(self):
        rows = [row[:-1] + ['Непознат текст'] for row in SENTENCE_ROWS]

        with self.assertRaises(DataProblems) as raised:
            import_tokens(self.write_file(rows))

        self.assertIn("title 'Непознат текст'", ' '.join(raised.exception.errors))
