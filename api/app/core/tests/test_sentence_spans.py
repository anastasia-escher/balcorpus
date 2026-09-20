"""Tests for knowing where each token sits inside the sentence it is read in."""

from django.test import TestCase

from core.processing.sentence_spans import join_tokens_with_spans

from .corpus_fixtures import Word

SEARCH_URL = '/api/v1/tokens/search/'


class JoinTokensWithSpansTests(TestCase):
    def spans_of(self, *words, field='source'):
        return join_tokens_with_spans(words, field)

    def test_the_text_is_the_sentence_as_it_is_read(self):
        text, _spans = self.spans_of(Word('Да', ud_id=1), Word('молим', ud_id=2))

        self.assertEqual(text, 'Да молим')

    def test_every_word_keeps_the_place_it_was_written_to(self):
        text, spans = self.spans_of(Word('Да', ud_id=1), Word('молим', ud_id=2))

        self.assertEqual(spans, {1: (0, 2), 2: (3, 8)})
        self.assertEqual(text[spans[2][0]:spans[2][1]], 'молим')

    def test_punctuation_keeps_the_place_it_was_glued_to(self):
        text, spans = self.spans_of(
            Word('Да', ud_id=1), Word('молим', ud_id=2), Word('.', ud_id=3)
        )

        self.assertEqual(text, 'Да молим.')
        self.assertEqual(spans[3], (8, 9))

    def test_the_same_form_twice_gets_two_places_of_its_own(self):
        # This is what the result list cannot work out from the string alone.
        text, spans = self.spans_of(
            Word('и', ud_id=1), Word('ние', ud_id=2), Word('и', ud_id=3)
        )

        self.assertEqual(text, 'и ние и')
        self.assertEqual(spans[1], (0, 1))
        self.assertEqual(spans[3], (6, 7))

    def test_a_word_the_corpus_does_not_have_gets_no_place(self):
        text, spans = self.spans_of(
            Word('Да', ud_id=1), Word(None, ud_id=2), Word('молим', ud_id=3)
        )

        self.assertEqual(text, 'Да молим')
        self.assertNotIn(2, spans)

    def test_no_tokens_give_an_empty_sentence_and_no_places(self):
        self.assertEqual(join_tokens_with_spans([], 'source'), ('', {}))
