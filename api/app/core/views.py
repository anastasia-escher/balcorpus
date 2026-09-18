import re

from django.db.models import F, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Text, Speaker, Sentence, Token
from .serializers import (
    TextSerializer,
    SpeakerSerializer,
    SentenceSerializer,
    TokenSerializer,
    TokenSearchResultSerializer,
)


def ud_relation(relation, prefix=''):
    """Match a UD relation together with its subtypes.

    Searching for "nsubj" should also find "nsubj:pass", because the search
    form only offers the base relations.  Example: ud_relation('nsubj') matches
    both "nsubj" and "nsubj:pass", but not "nsubj_other".
    """
    return (
        Q(**{f'{prefix}ud_type__iexact': relation})
        | Q(**{f'{prefix}ud_type__istartswith': f'{relation}:'})
    )


class CorpusPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'


class PublicCorpusViewSet(viewsets.ReadOnlyModelViewSet):
    """The corpus is public; only Django admin requires authentication."""

    permission_classes = [AllowAny]


class TextViewSet(PublicCorpusViewSet):
    queryset = Text.objects.all().prefetch_related(
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
        query = request.query_params.get('q', '').strip()
        lemma = request.query_params.get('lemma', '').strip()
        pos = request.query_params.get('pos', '').strip()
        ud = request.query_params.get('ud', '').strip()
        parent = request.query_params.get('parent', '').strip()

        if not any((query, lemma, pos, ud)):
            return Response(
                {'detail': 'Provide text, a lemma, a PoS tag, or a UD tag.'},
                status=400,
            )

        queryset = Token.objects.select_related(
            'sentence__speaker', 'sentence__text'
        ).prefetch_related('sentence__tokens')

        if query:
            queryset = queryset.filter(
                Q(source__icontains=query)
                | Q(diplomatic__icontains=query)
                | Q(lemma__icontains=query)
                | Q(sentence__text__text_name__icontains=query)
                | Q(sentence__text__short_description__icontains=query)
            )
        if lemma:
            queryset = queryset.filter(lemma__iexact=lemma)
        if pos:
            # MULTEXT-East tags support '?' as a single-character wildcard.
            pos_pattern = re.escape(pos).replace(r'\?', '.')
            queryset = queryset.filter(pos_tag__iregex=f'^{pos_pattern}$')
        if ud:
            queryset = queryset.filter(ud_relation(ud))
        if parent:
            # A token's head is the token of the same sentence whose ud_id
            # equals this token's head_ud_id.  Both conditions belong in one
            # filter() call so that they apply to the same related token.
            queryset = queryset.filter(
                ud_relation(parent, prefix='sentence__tokens__'),
                sentence__tokens__ud_id=F('head_ud_id'),
            )

        queryset = queryset.order_by('sentence__text_id', 'sentence__sentence_id', 'ud_id').distinct()
        page = self.paginate_queryset(queryset)
        serializer = TokenSearchResultSerializer(page or queryset, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
