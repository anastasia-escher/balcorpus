from rest_framework import serializers

from .models import Text, Sentence, Token, Speaker
from .processing import sentence_text

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = [
            'speaker_id', 'full_name', 'gender', 'place_of_birth', 'birthyear',
            'variety', 'education', 'religion', 'l1', 'l2', 'l3'
        ]

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = [
            'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos', 'pos_tag',
            'pos_ext', 'head_ud_id', 'ud_type', 'time'
        ]


class TokenSearchResultSerializer(serializers.ModelSerializer):
    """A token together with enough context to display a corpus match."""

    sentence_id = serializers.IntegerField(source='sentence.sentence_id', read_only=True)
    text_id = serializers.CharField(source='sentence.text.text_id', read_only=True)
    text_name = serializers.CharField(source='sentence.text.text_name', read_only=True)
    speaker_id = serializers.CharField(source='sentence.speaker.speaker_id', read_only=True, allow_null=True)
    speaker_name = serializers.CharField(source='sentence.speaker.full_name', read_only=True, allow_null=True)
    source_sentence = serializers.SerializerMethodField()
    diplomatic_sentence = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = [
            'id', 'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos',
            'pos_tag', 'pos_ext', 'head_ud_id', 'ud_type', 'time',
            'sentence_id', 'text_id', 'text_name', 'speaker_id', 'speaker_name',
            'source_sentence', 'diplomatic_sentence',
        ]

    def get_source_sentence(self, token):
        return sentence_text.source_text(token.sentence)

    def get_diplomatic_sentence(self, token):
        return sentence_text.diplomatic_text(token.sentence)

class SentenceSerializer(serializers.ModelSerializer):
    tokens = TokenSerializer(many=True, read_only=True)
    speaker = SpeakerSerializer(read_only=True)

    class Meta:
        model = Sentence
        fields = [
            'id', 'sentence_id', 'speaker', 'tokens'
        ]

class TextSerializer(serializers.ModelSerializer):
    sentences = SentenceSerializer(many=True, read_only=True)
    authors = SpeakerSerializer(many=True, read_only=True)

    class Meta:
        model = Text
        fields = [
            'text_id', 'source_number', 'text_name', 'data_genre', 'text_genre',
            'variety', 'text_date', 'source', 'short_description', 'authors',
            'sentences'
        ]
