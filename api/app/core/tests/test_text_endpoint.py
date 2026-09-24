"""Tests for the text list, which must not drag the whole corpus with it."""

from django.test import TestCase

from .corpus_fixtures import make_sentence, make_speaker, make_text

TEXTS_URL = '/api/v1/texts/'
COVERAGE_URL = '/api/v1/texts/coverage/'


class TextEndpointTests(TestCase):
    def setUp(self):
        text = make_text()
        self.speaker = make_speaker()
        text.authors.add(self.speaker)
        make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            text=text,
            speaker=self.speaker,
        )

    def test_a_text_carries_its_metadata_and_its_authors(self):
        result = self.client.get(TEXTS_URL).json()['results'][0]

        self.assertEqual(result['text_id'], 'panov_pechalbari_1936')
        self.assertEqual(result['text_name'], 'Печалбари')
        self.assertEqual(result['authors'][0]['speaker_id'], 'anton_panov')

    def test_a_hidden_speaker_shows_only_name_gender_and_languages(self):
        self.speaker.gender = 'М'
        self.speaker.l1 = 'mk'
        self.speaker.birthyear = 1905
        self.speaker.notes = 'ambassador'
        self.speaker.show_metadata = False
        self.speaker.save()

        author = self.client.get(TEXTS_URL).json()['results'][0]['authors'][0]

        self.assertEqual(author['full_name'], self.speaker.full_name)
        self.assertEqual(author['gender'], 'М')
        self.assertEqual(author['l1'], 'mk')
        self.assertIsNone(author['birthyear'])
        self.assertIsNone(author['notes'])

    def test_a_speaker_shows_all_details_by_default(self):
        self.speaker.birthyear = 1905
        self.speaker.save()

        author = self.client.get(TEXTS_URL).json()['results'][0]['authors'][0]

        self.assertEqual(author['birthyear'], 1905)

    def test_religion_is_never_shown(self):
        self.speaker.religion = 'Orthodox'
        self.speaker.save()

        author = self.client.get(TEXTS_URL).json()['results'][0]['authors'][0]

        self.assertNotIn('religion', author)

    def test_a_text_does_not_carry_its_sentences(self):
        # A text holds thousands of tokens; nesting them made this endpoint
        # answer with megabytes.
        result = self.client.get(TEXTS_URL).json()['results'][0]

        self.assertNotIn('sentences', result)
        self.assertNotIn('tokens', result)

    def test_one_text_on_its_own_does_not_carry_them_either(self):
        result = self.client.get(f'{TEXTS_URL}panov_pechalbari_1936/').json()

        self.assertNotIn('sentences', result)

    def test_a_text_says_whether_it_has_been_annotated(self):
        # The catalogue holds far more texts than the search can reach, so a
        # text has to say which of the two it is.
        make_text(text_id='krle_parite_1938', title='Парите')

        results = {text['text_id']: text['is_annotated']
                   for text in self.client.get(TEXTS_URL).json()['results']}

        self.assertTrue(results['panov_pechalbari_1936'])
        self.assertFalse(results['krle_parite_1938'])

    def test_the_coverage_says_how_much_of_the_catalogue_is_annotated(self):
        make_text(text_id='krle_parite_1938', title='Парите')

        answer = self.client.get(COVERAGE_URL).json()

        self.assertEqual(answer, {'total': 2, 'annotated': 1})

    def test_the_coverage_counts_a_text_once_however_many_sentences_it_has(self):
        text = make_text(text_id='krle_parite_1938', title='Парите')
        for number in (1, 2):
            make_sentence(
                'Парите се отепувачка', text=text, speaker=self.speaker, sentence_id=number
            )

        answer = self.client.get(COVERAGE_URL).json()

        self.assertEqual(answer, {'total': 2, 'annotated': 2})

    def test_the_list_is_paginated(self):
        answer = self.client.get(TEXTS_URL).json()

        self.assertIn('count', answer)
        self.assertIn('results', answer)

    def test_the_page_size_cannot_be_raised_without_limit(self):
        for number in range(2, 8):
            make_text(text_id=f'text_number_{number}', title=f'Текст {number}')

        answer = self.client.get(TEXTS_URL, {'page_size': 1000}).json()

        self.assertLessEqual(len(answer['results']), 100)
