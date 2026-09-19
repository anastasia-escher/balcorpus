"""Tests for putting a sentence back together out of its tokens."""

from django.test import TestCase

from core.processing.sentence_text import diplomatic_text, join_tokens, source_text

from .corpus_fixtures import make_sentence


class Word:
    """A stand-in for a Token, so the plain joining can be tested on its own."""

    def __init__(self, source=None, diplomatic=None):
        self.source = source
        self.diplomatic = diplomatic


class JoinTokensTests(TestCase):
    def test_words_are_separated_by_spaces(self):
        words = [Word('Да'), Word('молим')]
        self.assertEqual(join_tokens(words, 'source'), 'Да молим')

    def test_punctuation_sticks_to_the_word_before_it(self):
        words = [Word('Да'), Word('молим'), Word('.')]
        self.assertEqual(join_tokens(words, 'source'), 'Да молим.')

    def test_several_punctuation_marks_all_stick(self):
        words = [Word('Чувај'), Word('боже'), Word(','), Word('брани'), Word('!')]
        self.assertEqual(join_tokens(words, 'source'), 'Чувај боже, брани!')

    def test_punctuation_at_the_start_keeps_its_place(self):
        # There is no word in front of it to stick to.
        words = [Word('('), Word('Спиро')]
        self.assertEqual(join_tokens(words, 'source'), '( Спиро')

    def test_an_empty_word_is_skipped_rather_than_doubling_a_space(self):
        words = [Word('Да'), Word(None), Word('молим')]
        self.assertEqual(join_tokens(words, 'source'), 'Да молим')

    def test_no_tokens_give_an_empty_string(self):
        self.assertEqual(join_tokens([], 'source'), '')

    def test_a_field_the_corpus_does_not_have_gives_an_empty_string(self):
        words = [Word(source='Да'), Word(source='молим')]
        self.assertEqual(join_tokens(words, 'diplomatic'), '')


class SentenceTextTests(TestCase):
    def test_source_text_reads_the_sentence_as_it_was_written(self):
        sentence = make_sentence('Сè е во строг ред и чистота .')
        self.assertEqual(source_text(sentence), 'Сè е во строг ред и чистота.')

    def test_diplomatic_text_is_empty_when_the_corpus_has_none(self):
        sentence = make_sentence('Сè е во строг ред')
        self.assertEqual(diplomatic_text(sentence), '')
