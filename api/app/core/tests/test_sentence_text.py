"""Tests for putting a sentence back together out of its tokens."""

from django.test import TestCase

from core.processing.sentence_text import source_text

from .corpus_fixtures import make_sentence


class SentenceTextTests(TestCase):
    def test_source_text_reads_the_sentence_as_it_was_written(self):
        sentence = make_sentence('Сè е во строг ред и чистота .')
        self.assertEqual(source_text(sentence), 'Сè е во строг ред и чистота.')
