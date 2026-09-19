"""Tests for reading the sentences that stand around a search result."""

from django.test import TestCase

from core.processing.sentence_context import (
    DEFAULT_WINDOW,
    MAXIMUM_WINDOW,
    clamp_window,
    sentences_around,
)

from .corpus_fixtures import make_sentence, make_speaker, make_text

CONTEXT_URL = '/api/v1/sentences/context/'
TEXT_ID = 'panov_pechalbari_1936'


class ClampWindowTests(TestCase):
    def test_no_window_given_falls_back_to_the_default(self):
        self.assertEqual(clamp_window(None), DEFAULT_WINDOW)

    def test_a_window_that_is_too_large_is_cut_down(self):
        # Otherwise the endpoint is a way of downloading a whole text.
        self.assertEqual(clamp_window(1000), MAXIMUM_WINDOW)

    def test_a_negative_window_asks_for_nothing_either_side(self):
        self.assertEqual(clamp_window(-3), 0)

    def test_a_window_within_range_is_kept(self):
        self.assertEqual(clamp_window(1), 1)


class SentencesAroundTests(TestCase):
    """A short text, so that the edges of it can be tested."""

    def setUp(self):
        self.text = make_text()
        self.speaker = make_speaker()
        for number in range(1, 8):
            make_sentence(
                f'Реченица број {number}',
                text=self.text,
                speaker=self.speaker,
                sentence_id=number,
            )

    def numbers_around(self, sentence_number, window=DEFAULT_WINDOW):
        return list(
            sentences_around(self.text.text_id, sentence_number, window)
            .values_list('sentence_id', flat=True)
        )

    def test_the_window_reaches_two_sentences_either_side(self):
        self.assertEqual(self.numbers_around(4), [2, 3, 4, 5, 6])

    def test_the_sentence_itself_is_part_of_the_answer(self):
        self.assertIn(4, self.numbers_around(4))

    def test_at_the_start_of_a_text_the_window_is_simply_shorter(self):
        self.assertEqual(self.numbers_around(1), [1, 2, 3])

    def test_at_the_end_of_a_text_the_window_is_simply_shorter(self):
        self.assertEqual(self.numbers_around(7), [5, 6, 7])

    def test_a_window_of_zero_returns_only_the_sentence_itself(self):
        self.assertEqual(self.numbers_around(4, window=0), [4])

    def test_a_missing_number_is_skipped_rather_than_shifting_the_window(self):
        # Sentence 3 was dropped on import, as the byte-order-mark row was.
        self.text.sentences.filter(sentence_id=3).delete()
        self.assertEqual(self.numbers_around(4), [2, 4, 5, 6])

    def test_the_window_does_not_reach_into_another_text(self):
        other = make_text(text_id='krle_parite_1938', title='Парите')
        make_sentence('Туѓа реченица', text=other, speaker=self.speaker, sentence_id=5)

        around = sentences_around(self.text.text_id, 4)
        self.assertEqual({sentence.text_id for sentence in around}, {self.text.text_id})


class ContextEndpointTests(TestCase):
    def setUp(self):
        text = make_text()
        speaker = make_speaker()
        for number in range(1, 8):
            make_sentence(
                f'Реченица број {number}',
                text=text,
                speaker=speaker,
                sentence_id=number,
            )

    def context(self, **criteria):
        return self.client.get(CONTEXT_URL, criteria)

    def test_the_context_can_be_read_without_logging_in(self):
        self.assertEqual(self.context(text=TEXT_ID, sentence=4).status_code, 200)

    def test_the_answer_carries_the_readable_sentences(self):
        answer = self.context(text=TEXT_ID, sentence=4).json()

        self.assertEqual(answer['sentence_id'], 4)
        self.assertEqual(
            [row['sentence_id'] for row in answer['results']], [2, 3, 4, 5, 6]
        )
        self.assertEqual(answer['results'][0]['source_sentence'], 'Реченица број 2')
        self.assertEqual(answer['results'][0]['speaker_name'], 'Антон Панов')

    def test_the_window_can_be_narrowed(self):
        answer = self.context(text=TEXT_ID, sentence=4, window=1).json()

        self.assertEqual([row['sentence_id'] for row in answer['results']], [3, 4, 5])

    def test_the_window_cannot_be_widened_without_limit(self):
        answer = self.context(text=TEXT_ID, sentence=4, window=1000).json()

        self.assertLessEqual(len(answer['results']), 2 * MAXIMUM_WINDOW + 1)

    def test_a_request_without_a_text_is_refused(self):
        self.assertEqual(self.context(sentence=4).status_code, 400)

    def test_a_request_without_a_sentence_number_is_refused(self):
        self.assertEqual(self.context(text=TEXT_ID).status_code, 400)

    def test_a_sentence_number_that_is_not_a_number_is_refused(self):
        self.assertEqual(self.context(text=TEXT_ID, sentence='вторая').status_code, 400)

    def test_an_unknown_text_gives_an_empty_answer_and_not_an_error(self):
        answer = self.context(text='no_such_text_1900', sentence=4)

        self.assertEqual(answer.status_code, 200)
        self.assertEqual(answer.json()['results'], [])
