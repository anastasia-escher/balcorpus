from django.test import TestCase

from .models import Sentence, Speaker, Text, Token


class TokenSearchTests(TestCase):
    def setUp(self):
        text = Text.objects.create(text_name='Radio interview')
        speaker = Speaker.objects.create(speaker_id='ZZ', full_name='Zoran Zaev')
        sentence = Sentence.objects.create(text=text, sentence_id=1, speaker=speaker)
        Token.objects.create(
            sentence=sentence,
            ud_id=1,
            source='Да',
            diplomatic='Да',
            lemma='да',
            pos_tag='Q-s',
            ud_valency='2',
            pos_tag2='2',
            ud_type='aux',
        )
        Token.objects.create(
            sentence=sentence,
            ud_id=2,
            source='молим',
            diplomatic='молим',
            lemma='молим',
            pos_tag='I',
            ud_valency='0',
            ud_type='root',
        )

    def test_search_is_public_and_includes_sentence_context(self):
        response = self.client.get('/api/v1/tokens/search/', {'q': 'да'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        result = response.json()['results'][0]
        self.assertEqual(result['source_sentence'], 'Да молим')
        self.assertEqual(result['speaker_name'], 'Zoran Zaev')

    def test_ud_search_can_filter_by_the_parent_relation(self):
        response = self.client.get(
            '/api/v1/tokens/search/',
            {'ud': 'aux', 'parent': 'root'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['ud_type'], 'aux')
