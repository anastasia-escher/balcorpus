"""Tests for reading one text of the corpus, sentence by sentence."""

from django.test import TestCase

from .corpus_fixtures import make_sentence, make_speaker, make_text

SENTENCES_URL = '/api/v1/sentences/'
TEXT_ID = 'panov_pechalbari_1936'
OTHER_TEXT_ID = 'acevska_martinki_2008'


class SentenceEndpointTests(TestCase):
    """Two texts, so that one cannot quietly pick up the other's sentences."""

    def setUp(self):
        self.text = make_text()
        self.other_text = make_text(text_id=OTHER_TEXT_ID, title='Мартинки')
        self.speaker = make_speaker()

        make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            pos_tags=['Ncfsny', 'Vapip3s-n', 'Rgp', 'Ap-fs-n', 'Z'],
            text=self.text,
            speaker=self.speaker,
            sentence_id=1,
        )
        make_sentence(
            'Друг текст',
            text=self.other_text,
            speaker=self.speaker,
            sentence_id=1,
        )

    def sentences_of(self, text_id, **parameters):
        return self.client.get(SENTENCES_URL, {'text': text_id, **parameters}).json()

    def test_asking_for_a_text_leaves_the_rest_of_the_corpus_out(self):
        answer = self.sentences_of(TEXT_ID)

        self.assertEqual(answer['count'], 1)
        self.assertEqual(answer['results'][0]['sentence_id'], 1)

    def test_a_sentence_carries_its_tokens_with_their_annotation(self):
        # This is what the text page sets in grey under every word.
        first_token = self.sentences_of(TEXT_ID)['results'][0]['tokens'][0]

        self.assertEqual(first_token['source'], 'Комедијата')
        self.assertEqual(first_token['lemma'], 'комедија')
        self.assertEqual(first_token['pos_tag'], 'Ncfsny')

    def test_the_tokens_come_in_the_order_of_the_sentence(self):
        tokens = self.sentences_of(TEXT_ID)['results'][0]['tokens']

        self.assertEqual([token['ud_id'] for token in tokens], [1, 2, 3, 4, 5])

    def test_the_sentences_come_in_the_order_of_the_text(self):
        # Written out of order on purpose: the page needs them back in the
        # order of the text, not the order they were imported in.
        for number in [4, 2, 3]:
            make_sentence(
                f'Реченица број {number}',
                text=self.text,
                speaker=self.speaker,
                sentence_id=number,
            )

        numbers = [row['sentence_id'] for row in self.sentences_of(TEXT_ID)['results']]

        self.assertEqual(numbers, [1, 2, 3, 4])

    def test_a_text_nobody_has_imported_yet_answers_with_an_empty_page(self):
        answer = self.sentences_of('no_such_text_2099')

        self.assertEqual(answer['count'], 0)
        self.assertEqual(answer['results'], [])

    def test_without_a_text_the_whole_corpus_is_still_listed(self):
        answer = self.client.get(SENTENCES_URL).json()

        self.assertEqual(answer['count'], 2)

    def test_the_whole_corpus_is_ordered_by_text_and_then_by_sentence(self):
        # The list is paginated, so without a fixed order the same page number
        # could answer with different sentences from one request to the next.
        # 'acevska_martinki_2008' sorts before 'panov_pechalbari_1936', so its
        # one sentence comes first, then Печалбари's two in their own order.
        make_sentence('Втора', text=self.text, speaker=self.speaker, sentence_id=2)

        rows = self.client.get(SENTENCES_URL).json()['results']

        self.assertEqual([row['sentence_id'] for row in rows], [1, 1, 2])

    def test_the_text_is_handed_out_a_page_at_a_time(self):
        # A text of average length holds thousands of tokens, so the page must
        # never be able to ask for all of them at once.
        for number in range(2, 8):
            make_sentence(
                f'Реченица број {number}',
                text=self.text,
                speaker=self.speaker,
                sentence_id=number,
            )

        answer = self.sentences_of(TEXT_ID, page_size=3)

        self.assertEqual(answer['count'], 7)
        self.assertEqual(len(answer['results']), 3)
        self.assertIsNotNone(answer['next'])
