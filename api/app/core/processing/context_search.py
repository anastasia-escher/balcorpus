"""Searching for a token by what stands near it.

A form on its own is often not the question. The linguist asks for a first
person plural pronoun *that has a past tense verb two words in front of it*,
and wants both words back. This module adds that second condition to a search
that is otherwise built by ``token_search``.

The neighbour is found by position: tokens are numbered inside their sentence
by ``ud_id``, so the word two places in front of token 7 is token 5 of the
same sentence. Punctuation is a token like any other and therefore counts as
a position; "two words before" means two annotated tokens before.
"""

from django.db.models import OuterRef, Q, Subquery

from core.models import Token
from core.processing.token_search import criteria_filter

# How far from the searched word a neighbour may stand. Anything beyond this
# is no longer context: it is simply "somewhere in the same sentence", which
# is a different search and a much more expensive one.
MAXIMUM_DISTANCE = 3


def clamp_offset(offset):
    """Keep one end of the window within what the search is willing to look at.

    Example: clamp_offset(-2) -> -2, clamp_offset(9) -> 3
    """
    return max(-MAXIMUM_DISTANCE, min(offset, MAXIMUM_DISTANCE))


def offsets_between(offset_from, offset_to):
    """The distances a neighbour is allowed to stand at, both ends included.

    0 is left out: the searched token is not its own neighbour.

    Ends given the wrong way round describe the same window, so they are
    swapped rather than answered with nothing.

    Example: offsets_between(-3, -1) -> [-3, -2, -1]   three words before
             offsets_between(2, 2) -> [2]              exactly two words after
             offsets_between(2, -2) -> [-2, -1, 1, 2]  same as (-2, 2)
    """
    first = clamp_offset(offset_from)
    last = clamp_offset(offset_to)

    if first > last:
        first, last = last, first

    return [offset for offset in range(first, last + 1) if offset != 0]


def position_filter(offsets):
    """Match a token standing at one of the given distances from the searched one.

    This is written for the inside of a subquery, where ``OuterRef('ud_id')``
    is the number of the token being searched for. Each allowed distance is
    one plain equality, and they are joined by OR; with at most six of them
    that stays easier to read — and easier for the database — than arithmetic
    on a range.

    ``offsets`` must not be empty: an empty filter would let every token of
    the sentence through, turning "within three words" into "anywhere in the
    sentence".  ``add_context_condition`` is what keeps that from happening.
    """
    positions = Q()
    for offset in offsets:
        positions |= Q(ud_id=OuterRef('ud_id') + offset)

    return positions


def nearby_token_subquery(offsets, conditions):
    """The number of the neighbour that answers ``conditions``, or nothing.

    ``conditions`` is what describes the neighbour, built by
    ``token_search.criteria_filter`` so that a tag or a lemma is read exactly
    as it is read for the main word. Only the first match is taken, so a
    sentence where two words fit reports the earlier one.

    The subquery is tied to the outer token twice: same sentence, and a
    position measured from the outer token's own ``ud_id``. That is what keeps
    "two words before" relative to each match rather than absolute.
    """
    neighbours = (
        Token.objects
        .filter(position_filter(offsets), conditions)
        .filter(sentence=OuterRef('sentence'))
        .order_by('ud_id')
    )

    return Subquery(neighbours.values('ud_id')[:1])


def add_context_condition(queryset, offsets, criteria):
    """Keep only the tokens that have such a neighbour, and say which one it is.

    ``criteria`` describes the neighbour in the same words the main search
    uses: {'text': '', 'lemma': '', 'pos': 'Vmp*', 'ud': '', 'partial_text':
    False}.

    The neighbour's position is annotated as ``context_ud_id`` rather than
    looked up again afterwards: one subquery answers both questions, so the
    result carries the word to highlight without a second query per match.

    A condition that cannot be met — no word described, or a window that holds
    no position at all, as ``near_from=0&near_to=0`` does — answers with
    nothing.  Dropping it instead would hand back a search for the main word
    alone, which looks like an answer and is not the one that was asked for.
    """
    conditions = criteria_filter(**criteria)

    if not offsets or not conditions:
        return queryset.none()

    queryset = queryset.annotate(context_ud_id=nearby_token_subquery(offsets, conditions))

    return queryset.filter(context_ud_id__isnull=False)
