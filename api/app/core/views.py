from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Text, Speaker
from .processing.context_search import add_context_condition, offsets_between
from .processing.sentence_context import clamp_window, sentences_around
from .processing.text_search import build_text_queryset
from .processing.token_search import build_search_queryset
from .serializers import (
    TextSerializer,
    SpeakerSerializer,
    SentenceContextSerializer,
    TokenSearchResultSerializer,
)

# The ways a request can describe a word, as {parameter: name in the query}.
# A search needs at least one of them; 'parent' only narrows a result down
# further, so on its own it would ask for the whole corpus.
WORD_CRITERIA = {
    'q': 'text',
    'lemma': 'lemma',
    'pos': 'pos',
    'ud': 'ud',
}

# The word that has to stand near the match is described with the same
# parameters under this prefix, so that one request can describe both words:
# ?pos=Pp1-p*&near_pos=Vmp*&near_from=-2&near_to=-2
NEARBY_PREFIX = 'near_'

# Query parameters that are read as yes/no rather than as text.
TRUE_VALUES = {'1', 'true', 'yes', 'on'}


def read_flag(request, name):
    """Read a query parameter that means yes or no.

    Example: ?partial=true -> True, ?partial=0 -> False, absent -> False
    """
    return request.query_params.get(name, '').strip().lower() in TRUE_VALUES


def read_number(request, name):
    """Read a query parameter that should hold a whole number, or None."""
    value = request.query_params.get(name, '').strip()
    try:
        return int(value)
    except ValueError:
        return None


def read_word(request, prefix=''):
    """Read how the request describes one word.

    Without a prefix that is the word being searched for; with
    prefix=NEARBY_PREFIX it is the word that has to stand near it.

    Example: ?near_pos=Vmp* with prefix='near_' gives
    {'text': '', 'lemma': '', 'pos': 'Vmp*', 'ud': '', 'partial_text': False}
    """
    word = {
        name: request.query_params.get(prefix + parameter, '').strip()
        for parameter, name in WORD_CRITERIA.items()
    }
    word['partial_text'] = read_flag(request, prefix + 'partial')

    return word


def describes_a_word(word):
    """True when the request actually said which word it is looking for.

    ``partial_text`` is not part of the answer: on its own it only says how a
    word would be matched, not which word to look for.
    """
    return any(word[name] for name in WORD_CRITERIA.values())


def read_offsets(request):
    """The distances from the match the nearby word may stand at, e.g. [-2]."""
    # A missing end counts as 0, the word itself, so a request without a
    # distance finds nothing instead of failing.
    return offsets_between(
        read_number(request, NEARBY_PREFIX + 'from') or 0,
        read_number(request, NEARBY_PREFIX + 'to') or 0,
    )


class CorpusPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'


class PublicCorpusViewSet(viewsets.GenericViewSet):
    """Settings shared by every corpus endpoint.

    The corpus is public; only Django admin requires a login. This base
    deliberately brings no actions of its own: an endpoint can be listed, or
    read record by record, only if it asks for that.
    """

    permission_classes = [AllowAny]
    pagination_class = CorpusPagination


class BrowsableCorpusViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, PublicCorpusViewSet
):
    """A corpus endpoint whose records may be listed and read one by one.

    Only metadata is browsable this way. The annotated material is not: the
    corpus may not publish whole texts, and a paginated list of every sentence
    or every token is a whole text handed over a page at a time. Those two
    endpoints therefore offer nothing but their own bounded searches.
    """


class TextViewSet(BrowsableCorpusViewSet):
    # The sentences are not prefetched: TextSerializer does not carry them,
    # because a text holds thousands of tokens and a list of texts that
    # included them answered with megabytes.
    queryset = Text.objects.all().prefetch_related('authors')
    serializer_class = TextSerializer

    def get_queryset(self):
        """The catalogue, narrowed by ?q= to a title, an author or a text_id.

            /api/v1/texts/?q=панов
        """
        return build_text_queryset(self.request.query_params.get('q', ''))


class SpeakerViewSet(BrowsableCorpusViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer


class SentenceViewSet(PublicCorpusViewSet):
    """Sentences are not listed, only read a few at a time around a match.

    Listing them would be a way of downloading a text from beginning to end,
    which the corpus may not publish.
    """

    @action(detail=False, methods=['get'], url_path='context')
    def context(self, request):
        """The sentences standing around one sentence of a text.

        A concordance line is often not enough to judge a form, so the result
        list can ask for what came before and after it:

            /api/v1/sentences/context/?text=panov_pechalbari_1936&sentence=42

        The answer is short by design and therefore not paginated.
        """
        text_id = request.query_params.get('text', '').strip()
        sentence_number = read_number(request, 'sentence')

        if not text_id or sentence_number is None:
            return Response(
                {'detail': 'Provide a text and the number of a sentence in it.'},
                status=400,
            )

        sentences = sentences_around(
            text_id, sentence_number, clamp_window(read_number(request, 'window'))
        )
        serializer = SentenceContextSerializer(sentences, many=True)
        return Response({'sentence_id': sentence_number, 'results': serializer.data})


class TokenViewSet(PublicCorpusViewSet):
    """Tokens are not listed either, only searched.

    They carry the order they stand in, so a paginated list of all of them
    rebuilds every text exactly.
    """

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """Search token forms and their linguistic annotations.

        The endpoint deliberately returns a bounded, paginated result set.  The
        sentence context is included so the UI does not have to load the whole
        corpus before showing a match.

        A search may also describe a word that has to stand near the match,
        which is what the 'near_' parameters are for:

            ?pos=Pp1-p*&near_pos=Vmp*&near_from=-2&near_to=-2

        reads as "a first person plural pronoun with a past tense verb exactly
        two words in front of it".
        """
        searched_word = read_word(request)
        nearby_word = read_word(request, prefix=NEARBY_PREFIX)

        if not describes_a_word(searched_word):
            return Response(
                {'detail': 'Provide text, a lemma, a PoS tag, or a UD tag.'},
                status=400,
            )

        queryset = build_search_queryset(
            parent=request.query_params.get('parent', '').strip(),
            **searched_word,
        )

        if describes_a_word(nearby_word):
            queryset = add_context_condition(queryset, read_offsets(request), nearby_word)

        page = self.paginate_queryset(queryset)
        serializer = TokenSearchResultSerializer(page or queryset, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
