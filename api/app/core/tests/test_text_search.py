"""Tests for finding a text in the catalogue."""

from django.test import TestCase

from core.processing.text_search import build_text_queryset

from .corpus_fixtures import make_speaker, make_text

TEXTS_URL = '/api/v1/texts/'


class BuildTextQuerysetTests(TestCase):
    """A small catalogue, so that a search can be seen to exclude things."""

    def setUp(self):
        panov = make_speaker()
        acevska = make_speaker(speaker_id='vesna_acevska', name='Весна Ацевска')

        self.pechalbari = make_text()
        self.pechalbari.authors.add(panov)

        self.martinki = make_text(text_id='acevska_martinki_2008', title='Мартинки')
        self.martinki.authors.add(acevska)

    def found(self, query):
        return sorted(build_text_queryset(query).values_list('text_id', flat=True))

    def test_a_title_is_matched(self):
        self.assertEqual(self.found('Печалбари'), ['panov_pechalbari_1936'])

    def test_part_of_a_title_is_enough(self):
        self.assertEqual(self.found('чалба'), ['panov_pechalbari_1936'])

    def test_case_does_not_matter(self):
        self.assertEqual(self.found('печалбари'), ['panov_pechalbari_1936'])

    def test_an_author_is_matched(self):
        self.assertEqual(self.found('Ацевска'), ['acevska_martinki_2008'])

    def test_the_latin_text_id_is_matched_too(self):
        # The titles are in Cyrillic, so without this a reader typing on a
        # Latin keyboard could not find anything at all.
        self.assertEqual(self.found('pechalbari'), ['panov_pechalbari_1936'])

    def test_an_empty_query_gives_the_whole_catalogue(self):
        self.assertEqual(
            self.found(''), ['acevska_martinki_2008', 'panov_pechalbari_1936']
        )

    def test_a_query_of_only_spaces_gives_the_whole_catalogue(self):
        self.assertEqual(len(self.found('   ')), 2)

    def test_a_query_that_matches_nothing_gives_nothing(self):
        self.assertEqual(self.found('Достоевски'), [])

    def test_a_text_is_listed_once_even_with_several_matching_authors(self):
        # The join over a many-to-many column would otherwise repeat the text.
        second_author = make_speaker(speaker_id='kole_chashule', name='Коле Чашуле')
        self.pechalbari.authors.add(second_author)

        self.assertEqual(self.found('о'), sorted(self.found('о')))
        self.assertEqual(
            build_text_queryset('panov_pechalbari_1936').count(), 1
        )


class TextSearchEndpointTests(TestCase):
    def setUp(self):
        panov = make_speaker()
        pechalbari = make_text()
        pechalbari.authors.add(panov)

        for number in range(2, 9):
            make_text(text_id=f'other_text_{number}', title=f'Друг текст {number}')

    def test_searching_narrows_the_catalogue(self):
        answer = self.client.get(TEXTS_URL, {'q': 'Печалбари'}).json()

        self.assertEqual(answer['count'], 1)
        self.assertEqual(answer['results'][0]['text_id'], 'panov_pechalbari_1936')

    def test_searching_by_author_narrows_the_catalogue(self):
        answer = self.client.get(TEXTS_URL, {'q': 'Панов'}).json()

        self.assertEqual(answer['count'], 1)

    def test_a_search_result_still_carries_its_authors(self):
        answer = self.client.get(TEXTS_URL, {'q': 'Панов'}).json()

        self.assertEqual(answer['results'][0]['authors'][0]['speaker_id'], 'anton_panov')

    def test_without_a_query_the_whole_catalogue_is_listed(self):
        answer = self.client.get(TEXTS_URL).json()

        self.assertEqual(answer['count'], 8)

    def test_a_search_is_still_handed_out_a_page_at_a_time(self):
        answer = self.client.get(TEXTS_URL, {'q': 'текст', 'page_size': 3}).json()

        self.assertEqual(answer['count'], 7)
        self.assertEqual(len(answer['results']), 3)
        self.assertIsNotNone(answer['next'])

    def test_a_search_that_matches_nothing_answers_with_an_empty_page(self):
        answer = self.client.get(TEXTS_URL, {'q': 'Достоевски'}).json()

        self.assertEqual(answer['count'], 0)
        self.assertEqual(answer['results'], [])
