"""Tests for the search endpoint: what it answers, and how it pages."""

from django.test import TestCase

from .corpus_fixtures import make_sentence, make_speaker, make_text

SEARCH_URL = '/api/v1/tokens/search/'


class SearchEndpointTests(TestCase):
    def setUp(self):
        make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            pos_tags=['Ncfsny', 'Vapip3s-n', 'Rgp', 'Ap-fs-n', 'Z'],
            heads=[4, 4, 4, 0, 4],
            relations=['nsubj:pass', 'aux:pass', 'advmod', 'root', 'punct'],
        )

    def search(self, **criteria):
        return self.client.get(SEARCH_URL, criteria)

    def test_the_corpus_can_be_searched_without_logging_in(self):
        self.assertEqual(self.search(lemma='убав').status_code, 200)

    def test_a_search_without_criteria_is_refused(self):
        response = self.search()

        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.json())

    def test_a_parent_on_its_own_is_not_a_search(self):
        # It only narrows another criterion, so alone it would ask for the
        # whole corpus.
        self.assertEqual(self.search(parent='root').status_code, 400)

    def test_blank_criteria_count_as_no_criteria(self):
        self.assertEqual(self.search(lemma='   ').status_code, 400)

    def test_a_match_comes_back_with_its_sentence_and_its_speaker(self):
        result = self.search(lemma='убав').json()['results'][0]

        self.assertEqual(result['source'], 'убаво')
        self.assertEqual(result['source_sentence'], 'Комедијата е убаво напишана.')
        self.assertEqual(result['speaker_name'], 'Антон Панов')
        self.assertEqual(result['text_name'], 'Печалбари')

    def test_a_match_carries_its_annotation(self):
        result = self.search(lemma='комедија').json()['results'][0]

        self.assertEqual(result['pos_tag'], 'Ncfsny')
        self.assertEqual(result['ud_type'], 'nsubj:pass')
        self.assertEqual(result['head_ud_id'], 4)

    def test_nothing_found_is_an_empty_answer_and_not_an_error(self):
        response = self.search(lemma='нема-таква-лема')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)
        self.assertEqual(response.json()['results'], [])


class SearchPagingTests(TestCase):
    """The corpus answers one page at a time, so a large result stays small."""

    def setUp(self):
        text = make_text()
        speaker = make_speaker()
        # Sixty tokens, all sharing one lemma, so paging has something to do.
        for number in range(1, 13):
            make_sentence(
                'збор збор збор збор збор',
                lemmas=['збор'] * 5,
                text=text,
                speaker=speaker,
                sentence_id=number,
            )

    def page(self, **criteria):
        return self.client.get(SEARCH_URL, {'lemma': 'збор', **criteria}).json()

    def test_the_count_is_of_all_matches_not_of_the_page(self):
        answer = self.page(page_size=10)

        self.assertEqual(answer['count'], 60)
        self.assertEqual(len(answer['results']), 10)

    def test_a_page_can_be_asked_for_by_number(self):
        first = self.page(page_size=10, page=1)['results']
        second = self.page(page_size=10, page=2)['results']

        self.assertEqual(len(second), 10)
        self.assertNotEqual([token['id'] for token in first],
                            [token['id'] for token in second])

    def test_the_pages_together_are_the_whole_result(self):
        seen = []
        for number in range(1, 7):
            seen += [token['id'] for token in self.page(page_size=10, page=number)['results']]

        self.assertEqual(len(seen), 60)
        self.assertEqual(len(set(seen)), 60, 'a token turned up on two pages')

    def test_the_answer_says_whether_there_is_more(self):
        first = self.page(page_size=10, page=1)
        last = self.page(page_size=10, page=6)

        self.assertIsNotNone(first['next'])
        self.assertIsNone(first['previous'])
        self.assertIsNone(last['next'])
        self.assertIsNotNone(last['previous'])

    def test_a_page_past_the_end_is_not_found(self):
        response = self.client.get(SEARCH_URL, {'lemma': 'збор', 'page_size': 10, 'page': 99})

        self.assertEqual(response.status_code, 404)

    def test_the_page_size_cannot_be_raised_without_limit(self):
        # Otherwise one request could ask for the whole corpus at once.
        answer = self.page(page_size=1000)

        self.assertLessEqual(len(answer['results']), 100)
