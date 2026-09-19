"""Building the query behind the corpus search.

The view only reads the request and returns a page; everything that decides
*which* tokens match is written here.
"""

import re

from django.db.models import F, Q

from core.models import Token

# MULTEXT-East tags use '?' for "any character in this position", so a query
# like "N?sny" should find singular animate nouns of every gender.
POS_WILDCARD = '?'


def ud_relation_filter(relation, prefix=''):
    """Match a UD relation together with its subtypes.

    Searching for "nsubj" also finds "nsubj:pass", because the search form only
    offers the base relations.  ``prefix`` lets the same rule be applied to a
    related token, e.g. prefix='sentence__tokens__' for the head of a token.

    Example: ud_relation_filter('nsubj') matches "nsubj" and "nsubj:pass",
    but not "nsubjx".
    """
    return (
        Q(**{f'{prefix}ud_type__iexact': relation})
        | Q(**{f'{prefix}ud_type__istartswith': f'{relation}:'})
    )


def pos_tag_regex(pos):
    """Turn a MULTEXT-East query into a regular expression.

    Everything the user typed is escaped, so only '?' keeps a special meaning.

    Example: "N?sny" becomes "^N.sny$"
    """
    escaped = re.escape(pos)
    pattern = escaped.replace(re.escape(POS_WILDCARD), '.')
    return f'^{pattern}$'


def word_filter(text, partial=False):
    """Match a token by its written form or its lemma.

    By default the whole word has to match, which is what someone looking for
    a word form expects. ``partial`` widens it to "contains", for finding an
    ending or a stem: partial=True and text='ица' also finds "убавица".

    The metadata of the text — its title and description — are deliberately
    not searched here. They get a filter of their own; mixing them in meant
    that searching "Печалбари" returned all 13 989 tokens of the text called
    Печалбари instead of the eight that are the word.
    """
    if partial:
        return (
            Q(source__icontains=text)
            | Q(diplomatic__icontains=text)
            | Q(lemma__icontains=text)
        )

    return (
        Q(source__iexact=text)
        | Q(diplomatic__iexact=text)
        | Q(lemma__iexact=text)
    )


def head_filter(parent_relation):
    """Match tokens whose syntactic head carries the given UD relation.

    A token's head is the token of the same sentence whose ``ud_id`` equals
    this token's ``head_ud_id``.  Both conditions have to be passed to one
    filter() call so that they describe the same head token, not two
    different tokens that each satisfy one half.
    """
    return ud_relation_filter(parent_relation, prefix='sentence__tokens__')


def build_search_queryset(text='', lemma='', pos='', ud='', parent='', partial_text=False):
    """Return the tokens matching the given criteria, in corpus order.

    Empty criteria are simply skipped, so the caller can pass whatever the
    request contained.  The sentence and its tokens are fetched along with the
    result because every match is displayed together with its context.

    ``partial_text`` turns the free-text search from whole words into
    substrings; it has no effect on the other criteria.
    """
    queryset = Token.objects.select_related(
        'sentence__speaker', 'sentence__text'
    ).prefetch_related('sentence__tokens')

    if text:
        queryset = queryset.filter(word_filter(text, partial_text))
    if lemma:
        queryset = queryset.filter(lemma__iexact=lemma)
    if pos:
        queryset = queryset.filter(pos_tag__iregex=pos_tag_regex(pos))
    if ud:
        queryset = queryset.filter(ud_relation_filter(ud))
    if parent:
        queryset = queryset.filter(
            head_filter(parent),
            sentence__tokens__ud_id=F('head_ud_id'),
        )
        # Joining the sentence's tokens can repeat a row, so duplicates are
        # dropped.  Only this one filter joins, hence distinct() only here:
        # it costs a sort, and the other searches do not need it.
        queryset = queryset.distinct()

    return queryset.order_by('sentence__text_id', 'sentence__sentence_id', 'ud_id')
