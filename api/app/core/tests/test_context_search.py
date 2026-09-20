"""Tests for searching a word together with a word standing near it.

The example the feature was built for runs through the whole file: a first
person plural pronoun ('Pp1-p*') with a past tense verb ('Vmp*') two words in
front of it.
"""

from django.test import TestCase

from core.processing.context_search import (
    add_context_condition,
    clamp_offset,
    offsets_between,
)
from core.processing.token_search import build_search_queryset

from .corpus_fixtures import make_sentence, make_speaker, make_text

SEARCH_URL = '/api/v1/tokens/search/'

PRONOUN_TAG = 'Pp1-p'
PAST_VERB_TAG = 'Vmp3p'
PRESENT_VERB_TAG = 'Vmr1p'


class OffsetsTests(TestCase):
    """Which distances a neighbour may stand at."""

    def test_an_offset_within_reach_is_kept(self):
        self.assertEqual(clamp_offset(-2), -2)

    def test_an_offset_beyond_reach_is_pulled_back(self):
        self.assertEqual(clamp_offset(9), 3)
        self.assertEqual(clamp_offset(-9), -3)

    def test_a_window_of_one_position_is_an_exact_distance(self):
        self.assertEqual(offsets_between(-2, -2), [-2])

    def test_a_window_covers_everything_between_its_ends(self):
        self.assertEqual(offsets_between(-3, -1), [-3, -2, -1])

    def test_the_ends_may_be_given_in_either_order(self):
        self.assertEqual(offsets_between(-1, -3), [-3, -2, -1])

    def test_an_end_that_was_not_given_reaches_as_far_as_the_search_looks(self):
        self.assertEqual(offsets_between(), [-3, -2, -1, 1, 2, 3])

    def test_the_searched_word_is_not_its_own_neighbour(self):
        # 0 is the token itself, so a window across it leaves it out.
        self.assertEqual(offsets_between(-1, 1), [-1, 1])
        self.assertEqual(offsets_between(0, 0), [])


class ContextConditionTests(TestCase):
    """Which matches survive the condition about the nearby word."""

    def setUp(self):
        # "Yesterday we came, and we are going home."  The past tense verb
        # stands two words in front of the pronoun in the first sentence and
        # one word after it in the second.
        text = make_text()
        speaker = make_speaker()
        make_sentence(
            'Вчера дојдовме и ние .',
            lemmas=['вчера', 'дојде', 'и', 'ние', '.'],
            pos_tags=['Rgp', PAST_VERB_TAG, 'Ccs', PRONOUN_TAG, 'Z'],
            text=text,
            speaker=speaker,
            sentence_id=1,
        )
        make_sentence(
            'Ние одиме дома .',
            lemmas=['ние', 'оди', 'дома', '.'],
            pos_tags=[PRONOUN_TAG, PRESENT_VERB_TAG, 'Rgp', 'Z'],
            text=text,
            speaker=speaker,
            sentence_id=2,
        )

    def pronouns_with_a_neighbour(self, offsets, **neighbour):
        """The pronouns found, as (word form, position of the neighbour).

        A search that asked for no neighbour carries no position either, which
        is read here the way the serializer reads it.
        """
        queryset = add_context_condition(
            build_search_queryset(pos=f'{PRONOUN_TAG}*'), offsets, neighbour
        )

        return [(token.source, getattr(token, 'context_ud_id', None)) for token in queryset]

    def test_a_neighbour_is_found_at_the_exact_distance_asked_for(self):
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(-2, -2), pos='Vmp*'),
            [('ние', 2)],
        )

    def test_the_same_neighbour_is_found_inside_a_window(self):
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(-3, -1), pos='Vmp*'),
            [('ние', 2)],
        )

    def test_a_neighbour_at_another_distance_is_not_a_match(self):
        self.assertEqual(self.pronouns_with_a_neighbour(offsets_between(-1, -1), pos='Vmp*'), [])

    def test_the_side_of_the_window_matters(self):
        # The past tense verb of the first sentence stands before the pronoun,
        # so looking behind it finds nothing.
        self.assertEqual(self.pronouns_with_a_neighbour(offsets_between(1, 3), pos='Vmp*'), [])

    def test_a_neighbour_may_be_described_by_its_lemma(self):
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(-2, -2), lemma='дојде'),
            [('ние', 2)],
        )

    def test_a_neighbour_may_be_described_by_its_word_form(self):
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(1, 1), text='одиме'),
            [('Ние', 2)],
        )

    def test_a_word_is_not_its_own_neighbour(self):
        # Each sentence holds one such pronoun, so nothing may come back.
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(-3, 3), pos=f'{PRONOUN_TAG}*'),
            [],
        )

    def test_without_a_description_of_the_neighbour_nothing_is_narrowed(self):
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(-2, -2)),
            [('ние', None), ('Ние', None)],
        )

    def test_an_empty_window_narrows_nothing_either(self):
        self.assertEqual(
            self.pronouns_with_a_neighbour(offsets_between(0, 0), pos='Vmp*'),
            [('ние', None), ('Ние', None)],
        )


class SentenceBoundaryTests(TestCase):
    """A neighbour has to stand in the same sentence, not merely at the same
    position in another one."""

    def setUp(self):
        text = make_text()
        speaker = make_speaker()
        # The past tense verb is the first token of its sentence, and so is
        # the conjunction in front of the pronoun of the next sentence.
        make_sentence(
            'Молчеше .',
            pos_tags=[PAST_VERB_TAG, 'Z'],
            text=text,
            speaker=speaker,
            sentence_id=1,
        )
        make_sentence(
            'Ама ние молчиме .',
            pos_tags=['Ccs', PRONOUN_TAG, PRESENT_VERB_TAG, 'Z'],
            text=text,
            speaker=speaker,
            sentence_id=2,
        )

    def test_a_neighbour_from_the_previous_sentence_does_not_count(self):
        queryset = add_context_condition(
            build_search_queryset(pos=f'{PRONOUN_TAG}*'),
            offsets_between(-1, -1),
            {'pos': 'Vmp*'},
        )

        self.assertEqual(list(queryset), [])


class NearestNeighbourTests(TestCase):
    """When several words fit, the result names one of them."""

    def setUp(self):
        make_sentence(
            'Дојдовме и пеевме и ние .',
            pos_tags=['Vmp1p', 'Ccs', PAST_VERB_TAG, 'Ccs', PRONOUN_TAG, 'Z'],
        )

    def test_the_first_fitting_word_of_the_sentence_is_reported(self):
        queryset = add_context_condition(
            build_search_queryset(pos=f'{PRONOUN_TAG}*'),
            offsets_between(-4, -1),
            {'pos': 'Vmp*'},
        )
        match = queryset.get()

        # Both verbs stand within the window; the earlier one is the answer,
        # and the window itself was pulled back to three words.
        self.assertEqual(match.source, 'ние')
        self.assertEqual(match.context_ud_id, 3)


class ContextSearchEndpointTests(TestCase):
    """The same search asked over HTTP."""

    def setUp(self):
        make_sentence(
            'Вчера дојдовме и ние .',
            lemmas=['вчера', 'дојде', 'и', 'ние', '.'],
            pos_tags=['Rgp', PAST_VERB_TAG, 'Ccs', PRONOUN_TAG, 'Z'],
        )

    def search(self, **criteria):
        return self.client.get(SEARCH_URL, criteria)

    def test_a_match_carries_the_word_found_beside_it(self):
        response = self.search(
            pos=f'{PRONOUN_TAG}*', near_pos='Vmp*', near_from=-2, near_to=-2
        )
        result = response.json()['results'][0]

        self.assertEqual(result['source'], 'ние')
        self.assertEqual(result['context_ud_id'], 2)
        self.assertEqual(result['context_source'], 'дојдовме')

    def test_a_search_for_one_word_alone_has_no_such_word(self):
        result = self.search(pos=f'{PRONOUN_TAG}*').json()['results'][0]

        self.assertIsNone(result['context_ud_id'])
        self.assertIsNone(result['context_source'])

    def test_the_condition_narrows_the_result(self):
        response = self.search(
            pos=f'{PRONOUN_TAG}*', near_pos='Vmp*', near_from=1, near_to=3
        )

        self.assertEqual(response.json()['count'], 0)

    def test_a_distance_without_a_word_to_look_for_is_refused(self):
        response = self.search(pos=f'{PRONOUN_TAG}*', near_from=-2, near_to=-2)

        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.json())

    def test_a_neighbour_without_a_distance_is_looked_for_all_around(self):
        result = self.search(pos=f'{PRONOUN_TAG}*', near_pos='Vmp*').json()['results'][0]

        self.assertEqual(result['context_ud_id'], 2)
