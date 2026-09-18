from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Text, Speaker, Sentence, Token
from .processing.token_search import build_search_queryset
from .serializers import (
    TextSerializer,
    SpeakerSerializer,
    SentenceSerializer,
    TokenSerializer,
    TokenSearchResultSerializer,
)

# The criteria a search needs at least one of; 'parent' only narrows a result
# down further, so on its own it would ask for the whole corpus.
SEARCH_CRITERIA = ['q', 'lemma', 'pos', 'ud']


class CorpusPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'


class PublicCorpusViewSet(viewsets.ReadOnlyModelViewSet):
    """The corpus is public; only Django admin requires authentication."""

    permission_classes = [AllowAny]


class TextViewSet(PublicCorpusViewSet):
    queryset = Text.objects.all().prefetch_related(
        'authors',
        'sentences__tokens',
        'sentences__speaker',
    )
    serializer_class = TextSerializer


class SpeakerViewSet(PublicCorpusViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer


class SentenceViewSet(PublicCorpusViewSet):
    queryset = Sentence.objects.all().select_related('speaker', 'text').prefetch_related('tokens')
    serializer_class = SentenceSerializer


class TokenViewSet(PublicCorpusViewSet):
    queryset = Token.objects.all().select_related('sentence__speaker', 'sentence__text')
    serializer_class = TokenSerializer
    pagination_class = CorpusPagination

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
        )

        page = self.paginate_queryset(queryset)
        serializer = TokenSearchResultSerializer(page or queryset, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
