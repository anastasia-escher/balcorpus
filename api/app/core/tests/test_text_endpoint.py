"""Tests for the text list, which must not drag the whole corpus with it."""

from django.test import TestCase

from .corpus_fixtures import make_sentence, make_speaker, make_text

TEXTS_URL = '/api/v1/texts/'


class TextEndpointTests(TestCase):
    def setUp(self):
        text = make_text()
        speaker = make_speaker()
        text.authors.add(speaker)
        make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            text=text,
            speaker=speaker,
        )

    def test_a_text_carries_its_metadata_and_its_authors(self):
        result = self.client.get(TEXTS_URL).json()['results'][0]

        self.assertEqual(result['text_id'], 'panov_pechalbari_1936')
        self.assertEqual(result['text_name'], 'Печалбари')
        self.assertEqual(result['authors'][0]['speaker_id'], 'anton_panov')

    def test_a_text_does_not_carry_its_sentences(self):
        # A text holds thousands of tokens; nesting them made this endpoint
        # answer with megabytes.
        result = self.client.get(TEXTS_URL).json()['results'][0]

        self.assertNotIn('sentences', result)
        self.assertNotIn('tokens', result)

    def test_one_text_on_its_own_does_not_carry_them_either(self):
        result = self.client.get(f'{TEXTS_URL}panov_pechalbari_1936/').json()

        self.assertNotIn('sentences', result)

    def test_the_list_is_paginated(self):
        answer = self.client.get(TEXTS_URL).json()

        self.assertIn('count', answer)
        self.assertIn('results', answer)

    def test_the_page_size_cannot_be_raised_without_limit(self):
        for number in range(2, 8):
            make_text(text_id=f'text_number_{number}', title=f'Текст {number}')

        answer = self.client.get(TEXTS_URL, {'page_size': 1000}).json()

        self.assertLessEqual(len(answer['results']), 100)
