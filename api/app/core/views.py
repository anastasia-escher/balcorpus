from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Text, Speaker, Sentence, Token
from .processing.sentence_context import clamp_window, sentences_around
from .processing.text_search import build_text_queryset
from .processing.text_sentences import sentences_of_text
from .processing.token_search import build_search_queryset
from .serializers import (
    TextSerializer,
    SpeakerSerializer,
    SentenceSerializer,
    SentenceContextSerializer,
    TokenSerializer,
    TokenSearchResultSerializer,
)

# The criteria a search needs at least one of; 'parent' only narrows a result
# down further, so on its own it would ask for the whole corpus.
SEARCH_CRITERIA = ['q', 'lemma', 'pos', 'ud']

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


class CorpusPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'


class PublicCorpusViewSet(viewsets.ReadOnlyModelViewSet):
    """The corpus is public; only Django admin requires authentication."""

    permission_classes = [AllowAny]
    pagination_class = CorpusPagination


class TextViewSet(PublicCorpusViewSet):
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


class SpeakerViewSet(PublicCorpusViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer


class SentenceViewSet(PublicCorpusViewSet):
    queryset = Sentence.objects.all().select_related('speaker', 'text').prefetch_related('tokens')
    serializer_class = SentenceSerializer

    def get_queryset(self):
        """The whole corpus, or one text of it when ?text= names one.

        Reading a text is what the text page does:

            /api/v1/sentences/?text=panov_pechalbari_1936
        """
        text_id = self.request.query_params.get('text', '').strip()

        if text_id:
            return sentences_of_text(text_id)

        return super().get_queryset()

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
    queryset = Token.objects.all().select_related('sentence__speaker', 'sentence__text')
    serializer_class = TokenSerializer

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """Search token forms and their linguistic annotations.

        The endpoint deliberately returns a bounded, paginated result set.  The
        sentence context is included so the UI does not have to load the whole
        corpus before showing a match.
        """
        criteria = {
            name: request.query_params.get(name, '').strip()
            for name in SEARCH_CRITERIA + ['parent']
        }

        if not any(criteria[name] for name in SEARCH_CRITERIA):
            return Response(
                {'detail': 'Provide text, a lemma, a PoS tag, or a UD tag.'},
                status=400,
            )

        queryset = build_search_queryset(
            text=criteria['q'],
            lemma=criteria['lemma'],
            pos=criteria['pos'],
            ud=criteria['ud'],
            parent=criteria['parent'],
            partial_text=read_flag(request, 'partial'),
        )

        page = self.paginate_queryset(queryset)
        serializer = TokenSearchResultSerializer(page or queryset, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
