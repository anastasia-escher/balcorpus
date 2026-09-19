"""Tests for the pieces that decide which tokens a search matches."""

from django.test import TestCase

from core.models import Token
from core.processing.token_search import (
    build_search_queryset,
    pos_tag_regex,
    ud_relation_filter,
)

from .corpus_fixtures import make_sentence, make_speaker, make_text


class PosTagRegexTests(TestCase):
    """The MULTEXT-East query language: letters, and '?' for any letter."""

    def test_a_plain_tag_matches_only_itself(self):
        self.assertEqual(pos_tag_regex('Ncfsnn'), '^Ncfsnn$')

    def test_a_question_mark_stands_for_one_character(self):
        self.assertEqual(pos_tag_regex('N?sny'), '^N.sny$')

    def test_other_regular_expression_characters_lose_their_meaning(self):
        # A dot the user typed is escaped, so it means a dot and not
        # "any character". Only '?' keeps a special meaning.
        self.assertEqual(pos_tag_regex('Ap-fs-n'), r'^Ap\-fs\-n$')
        self.assertEqual(pos_tag_regex('A.b'), r'^A\.b$')


class UdRelationFilterTests(TestCase):
    """Searching a relation finds its subtypes, because the form offers only
    the base relations."""

    def setUp(self):
        make_sentence(
            'Комедијата е убаво напишана',
            relations=['nsubj:pass', 'aux:pass', 'advmod', 'root'],
            heads=[4, 4, 4, 0],
        )

    def forms_matching(self, *args, **kwargs):
        return sorted(
            Token.objects.filter(ud_relation_filter(*args, **kwargs))
            .values_list('source', flat=True)
        )

    def test_a_base_relation_also_finds_its_subtypes(self):
        self.assertEqual(self.forms_matching('nsubj'), ['Комедијата'])

    def test_a_relation_without_subtypes_matches_exactly(self):
        self.assertEqual(self.forms_matching('advmod'), ['убаво'])

    def test_a_relation_does_not_match_a_longer_name(self):
        # 'aux' must not be found by searching for 'au'.
        self.assertEqual(self.forms_matching('au'), [])


class SearchQuerysetTests(TestCase):
    """The filters the search endpoint offers, over a small corpus."""

    def setUp(self):
        self.sentence = make_sentence(
            'Комедијата е убаво напишана .',
            lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
            pos_tags=['Ncfsny', 'Vapip3s-n', 'Rgp', 'Ap-fs-n', 'Z'],
            heads=[4, 4, 4, 0, 4],
            relations=['nsubj:pass', 'aux:pass', 'advmod', 'root', 'punct'],
        )

    def forms(self, **criteria):
        return sorted(build_search_queryset(**criteria).values_list('source', flat=True))

    def test_free_text_matches_a_whole_word_form(self):
        self.assertEqual(self.forms(text='убаво'), ['убаво'])

    def test_free_text_matches_a_whole_lemma(self):
        self.assertEqual(self.forms(text='убав'), ['убаво'])

    def test_free_text_does_not_match_part_of_a_word_by_default(self):
        # Someone looking for a word form wants that form, not every word it
        # happens to sit inside.
        self.assertEqual(self.forms(text='комеди'), [])

    def test_partial_text_matches_part_of_a_word(self):
        self.assertEqual(self.forms(text='комеди', partial_text=True), ['Комедијата'])

    def test_partial_text_matches_an_ending(self):
        self.assertEqual(self.forms(text='ата', partial_text=True), ['Комедијата'])

    def test_free_text_does_not_search_the_metadata_of_the_text(self):
        # The title of the text is 'Печалбари'. Matching it here used to
        # return every token of the text; the metadata get their own filter.
        self.assertEqual(self.forms(text='Печалбари'), [])
        self.assertEqual(self.forms(text='Печалбари', partial_text=True), [])

    def test_lemma_matches_the_whole_lemma_only(self):
        self.assertEqual(self.forms(lemma='убав'), ['убаво'])
        self.assertEqual(self.forms(lemma='убa'), [])

    def test_lemma_ignores_capitals(self):
        self.assertEqual(self.forms(lemma='КОМЕДИЈА'), ['Комедијата'])

    def test_pos_tag_matches_a_full_tag(self):
        self.assertEqual(self.forms(pos='Ncfsny'), ['Комедијата'])

    def test_pos_tag_wildcard_matches_one_position(self):
        self.assertEqual(self.forms(pos='Ap-?s-n'), ['напишана'])

    def test_pos_tag_matches_the_whole_tag_not_a_prefix(self):
        # 'N' alone must not find 'Ncfsny': the pattern is anchored.
        self.assertEqual(self.forms(pos='N'), [])

    def test_ud_relation_includes_subtypes(self):
        self.assertEqual(self.forms(ud='nsubj'), ['Комедијата'])

    def test_parent_narrows_a_relation_to_a_given_head(self):
        self.assertEqual(self.forms(ud='nsubj', parent='root'), ['Комедијата'])

    def test_parent_that_does_not_occur_matches_nothing(self):
        self.assertEqual(self.forms(ud='nsubj', parent='obj'), [])

    def test_parent_looks_at_the_head_and_not_at_any_token(self):
        # 'advmod' is in the sentence, but it is nobody's head here.
        self.assertEqual(self.forms(ud='nsubj', parent='advmod'), [])

    def test_criteria_are_combined(self):
        self.assertEqual(self.forms(lemma='убав', ud='advmod'), ['убаво'])
        self.assertEqual(self.forms(lemma='убав', ud='root'), [])

    def test_no_criteria_returns_the_whole_corpus(self):
        # The endpoint refuses an empty search; the queryset itself does not
        # have an opinion about it.
        self.assertEqual(len(self.forms()), 5)

    def test_results_come_back_in_the_order_of_the_corpus(self):
        # 'а' is inside four of the five words, in corpus order.
        forms = list(
            build_search_queryset(text='а', partial_text=True)
            .values_list('source', flat=True)
        )
        self.assertEqual(forms, ['Комедијата', 'убаво', 'напишана'])

    def test_a_token_is_not_repeated_when_filtering_by_parent(self):
        # Joining the sentence's tokens can produce the same row twice.
        make_sentence(
            'Тој чита книга',
            heads=[2, 0, 2],
            relations=['nsubj', 'root', 'obj'],
            text=self.sentence.text,
            speaker=self.sentence.speaker,
            sentence_id=2,
        )
        self.assertEqual(self.forms(ud='obj', parent='root'), ['книга'])

    def test_searches_do_not_cross_into_another_text(self):
        other_text = make_text(text_id='krle_parite_1938', title='Парите')
        other_speaker = make_speaker(speaker_id='risto_krle', name='Ристо Крле')
        make_sentence(
            'Парите се отепувачка',
            lemmas=['пари', 'се', 'отепувачка'],
            text=other_text,
            speaker=other_speaker,
        )
        self.assertEqual(self.forms(lemma='пари'), ['Парите'])
