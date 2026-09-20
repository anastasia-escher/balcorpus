"""Building a small corpus for a test to search through.

Writing out four model objects by hand in every test buries what the test is
actually about, so a test says what it needs in one line:

    make_sentence(
        'Комедијата е убаво напишана .',
        lemmas=['комедија', 'сум', 'убав', 'напишан', '.'],
        pos_tags=['Ncfsny', 'Vapip3s-n', 'Rgp', 'Ap-fs-n', 'Z'],
        heads=[4, 4, 4, 0, 4],
        relations=['nsubj:pass', 'aux:pass', 'advmod', 'root', 'punct'],
    )
"""

from core.models import Sentence, Speaker, Text, Token

DEFAULT_TEXT_ID = 'panov_pechalbari_1936'
DEFAULT_TITLE = 'Печалбари'
DEFAULT_SPEAKER_ID = 'anton_panov'
DEFAULT_SPEAKER_NAME = 'Антон Панов'


class Word:
    """A stand-in for a Token, so that putting a sentence back together can be
    tested without writing four model objects to the database.

    Example: Word('молим', ud_id=2)
    """

    def __init__(self, source=None, diplomatic=None, ud_id=1):
        self.source = source
        self.diplomatic = diplomatic
        self.ud_id = ud_id


def make_text(text_id=DEFAULT_TEXT_ID, title=DEFAULT_TITLE, **fields):
    """One text of the corpus."""
    return Text.objects.create(text_id=text_id, text_name=title, **fields)


def make_speaker(speaker_id=DEFAULT_SPEAKER_ID, name=DEFAULT_SPEAKER_NAME, **fields):
    """One speaker of the corpus."""
    return Speaker.objects.create(speaker_id=speaker_id, full_name=name, **fields)


def make_sentence(
    words,
    lemmas=None,
    pos_tags=None,
    heads=None,
    relations=None,
    ud_parts_of_speech=None,
    text=None,
    speaker=None,
    sentence_id=1,
):
    """One sentence, with a token per word of ``words``.

    ``words`` is the sentence as a string, split on spaces. Every other list
    runs parallel to it, and whatever is left out simply stays empty.
    """
    forms = words.split()
    text = text or make_text()
    speaker = speaker or make_speaker()
    sentence = Sentence.objects.create(text=text, sentence_id=sentence_id, speaker=speaker)

    def value(values, position):
        return values[position] if values and position < len(values) else None

    Token.objects.bulk_create([
        Token(
            sentence=sentence,
            ud_id=position + 1,
            source=form,
            lemma=value(lemmas, position),
            ud_pos=value(ud_parts_of_speech, position),
            pos_tag=value(pos_tags, position),
            head_ud_id=value(heads, position),
            ud_type=value(relations, position),
        )
        for position, form in enumerate(forms)
    ])

    return sentence
