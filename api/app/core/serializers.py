from rest_framework import serializers

from .models import Text, Sentence, Token, Speaker
from .processing import sentence_spans, sentence_text

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = [
            'speaker_id', 'full_name', 'birth_name', 'gender', 'birthyear',
            'place_of_birth', 'place_type', 'municipality', 'dialect_region',
            'education_level', 'education_note', 'religion', 'l1', 'l2', 'l3',
            'notes',
        ]

class TokenSearchResultSerializer(serializers.ModelSerializer):
    """A token together with enough context to display a corpus match."""

    sentence_id = serializers.IntegerField(source='sentence.sentence_id', read_only=True)
    text_id = serializers.CharField(source='sentence.text.text_id', read_only=True)
    text_name = serializers.CharField(source='sentence.text.text_name', read_only=True)
    speaker_id = serializers.CharField(source='sentence.speaker.speaker_id', read_only=True, allow_null=True)
    speaker_name = serializers.CharField(source='sentence.speaker.full_name', read_only=True, allow_null=True)
    # The sentence the match stands in, in the reading the list shows.
    sentence = serializers.SerializerMethodField()
    # The second word of the match, when the search asked for one standing
    # nearby. Both are None for a search that did not ask.
    context_ud_id = serializers.SerializerMethodField()
    context_source = serializers.SerializerMethodField()
    # Where the two words sit in the sentence above, so that the result list
    # can mark them without searching the string for them again.
    match_span = serializers.SerializerMethodField()
    context_span = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = [
            'id', 'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos',
            'pos_tag', 'pos_ext', 'head_ud_id', 'ud_type', 'time',
            'sentence_id', 'text_id', 'text_name', 'speaker_id', 'speaker_name',
            'sentence', 'context_ud_id', 'context_source', 'match_span', 'context_span',
        ]

    def get_sentence(self, token):
        text, _spans = sentence_spans.displayed_sentence(token.sentence.tokens.all())
        return text

    def get_context_ud_id(self, token):
        # Annotated by context_search, so it is simply absent from a search
        # that asked for one word only.
        return getattr(token, 'context_ud_id', None)

    def get_context_source(self, token):
        """The written form of the nearby word, e.g. "дојдовме".

        Read the way the sentence around it is read: the source form, or the
        diplomatic transcription for a text that has no source.  Otherwise the
        word could be marked in the sentence and yet named nowhere.
        """
        neighbour = self.find_context_token(token)
        if not neighbour:
            return None

        return neighbour.source or neighbour.diplomatic

    def get_match_span(self, token):
        """Where the matched word stands in ``sentence``, as [start, end], or None."""
        return self.span_of(token, token.ud_id)

    def get_context_span(self, token):
        """Where the word found beside it stands, or None."""
        context_ud_id = self.get_context_ud_id(token)
        if context_ud_id is None:
            return None

        return self.span_of(token, context_ud_id)

    def span_of(self, token, ud_id):
        """Where the token numbered ``ud_id`` stands in this result's sentence."""
        _text, spans = sentence_spans.displayed_sentence(token.sentence.tokens.all())
        return spans.get(ud_id)

    def find_context_token(self, token):
        """The token the search found beside this one, or None.

        The sentence's tokens are already prefetched for the readable text, so
        the neighbour is picked out of them here instead of being fetched
        again per result.
        """
        context_ud_id = self.get_context_ud_id(token)
        if context_ud_id is None:
            return None

        for candidate in token.sentence.tokens.all():
            if candidate.ud_id == context_ud_id:
                return candidate

        return None

class SentenceContextSerializer(serializers.ModelSerializer):
    """One sentence standing next to a search result, ready to read."""

    speaker_name = serializers.CharField(source='speaker.full_name', read_only=True, allow_null=True)
    source_sentence = serializers.SerializerMethodField()

    class Meta:
        model = Sentence
        fields = ['sentence_id', 'speaker_name', 'source_sentence']

    def get_source_sentence(self, sentence):
        return sentence_text.source_text(sentence)


class TextSerializer(serializers.ModelSerializer):
    """A text and its metadata.

    The sentences are deliberately not nested here.  A text of average length
    carries some fourteen thousand tokens, so a list of texts that included
    them answered with megabytes; the sentences are read through
    /sentences/ and /tokens/search/ instead.
    """

    authors = SpeakerSerializer(many=True, read_only=True)
    # Whether the text has been annotated, and so whether the search reaches
    # it. Counted on the queryset by build_text_queryset, not stored.
    is_annotated = serializers.BooleanField(read_only=True)

    class Meta:
        model = Text
        fields = [
            'text_id', 'text_name', 'data_genre', 'text_genre', 'variety',
            'variety_note', 'text_date', 'year_note', 'source',
            'short_description', 'authors', 'is_annotated',
        ]
