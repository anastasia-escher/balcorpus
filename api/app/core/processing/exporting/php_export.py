"""Which tables of the corpus go into which file, and in which columns.

The metadata is written whole, the annotation one file per text.  That is what
makes adding a text to the server cheap: a newly annotated text is two small
files to copy, not the whole corpus again.

No numeric database key is ever written.  Re-importing a text deletes its
sentences and tokens and creates them again, so their ``id`` is a different
number after every import and would mean nothing on the server.  The files
therefore refer to a text by its ``text_id``, to a person by their
``speaker_id``, to a sentence by its number within the text and to a token by
its number within the sentence -- the same names the linguists use.
"""

from pathlib import Path

from core.models import Sentence, Speaker, Text, Token

from .csv_writer import write_csv

SPEAKERS_FILE = 'speakers.csv'
TEXTS_FILE = 'texts.csv'
TEXT_AUTHORS_FILE = 'text_authors.csv'
SENTENCES_FOLDER = 'sentences'
TOKENS_FOLDER = 'tokens'

SPEAKER_COLUMNS = (
    'speaker_id', 'full_name', 'birth_name', 'gender', 'birthyear',
    'place_of_birth', 'place_type', 'municipality', 'dialect_region',
    'education_level', 'education_note', 'religion', 'l1', 'l2', 'l3',
    'notes', 'source_row',
)

TEXT_COLUMNS = (
    'text_id', 'source_number', 'text_name', 'data_genre', 'text_genre',
    'variety', 'variety_note', 'text_date', 'year_note', 'source',
    'source_file', 'short_description',
)

# Who wrote a text: the many-to-many table, as the two slugs it joins.
TEXT_AUTHOR_COLUMNS = ('text_id', 'speaker_id')

SENTENCE_COLUMNS = ('text_id', 'sentence_id', 'speaker_id')

# The columns of a token that belong to the token itself; the two that place
# it in the corpus are added in front of them.
TOKEN_FIELDS = (
    'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos', 'pos_tag',
    'pos_ext', 'head_ud_id', 'ud_type', 'time',
)

TOKEN_COLUMNS = ('text_id', 'sentence_id') + TOKEN_FIELDS


def speaker_rows():
    """Every person of the corpus, one dict per row."""
    return Speaker.objects.values(*SPEAKER_COLUMNS).iterator()


def text_rows():
    """Every document of the corpus together with its metadata."""
    return Text.objects.values(*TEXT_COLUMNS).iterator()


def text_author_rows():
    """Every author-of-a-text pair, as two slugs.

    Example: {'text_id': 'panov_pechalbari_1936', 'speaker_id': 'anton_panov'}
    """
    pairs = (
        Text.objects
        .filter(authors__isnull=False)
        .order_by('text_id', 'authors__speaker_id')
        .values_list('text_id', 'authors__speaker_id')
    )

    for text_id, speaker_id in pairs.iterator():
        yield {'text_id': text_id, 'speaker_id': speaker_id}


def sentence_rows(text_id):
    """The sentences of one text, in the order the text is written.

    Example: {'text_id': 'panov_pechalbari_1936', 'sentence_id': 42,
              'speaker_id': 'anton_panov'}
    """
    sentences = (
        Sentence.objects
        .filter(text_id=text_id)
        .order_by('sentence_id')
        .values_list('sentence_id', 'speaker__speaker_id')
    )

    for sentence_id, speaker_id in sentences.iterator():
        yield {
            'text_id': text_id,
            'sentence_id': sentence_id,
            'speaker_id': speaker_id,
        }


def token_rows(text_id):
    """Every annotated word of one text, in corpus order."""
    tokens = (
        Token.objects
        .filter(sentence__text_id=text_id)
        .order_by('sentence__sentence_id', 'ud_id')
        .values('sentence__sentence_id', *TOKEN_FIELDS)
    )

    for token in tokens.iterator():
        token['text_id'] = text_id
        token['sentence_id'] = token.pop('sentence__sentence_id')
        yield token


def annotated_text_ids():
    """The texts an annotation has been imported for, in corpus order.

    A text whose annotation has not arrived yet has metadata but no sentences,
    and there is nothing to write for it.
    """
    return (
        Text.objects
        .filter(sentences__isnull=False)
        .order_by('text_id')
        .values_list('text_id', flat=True)
        .distinct()
    )


def export_metadata(output_folder):
    """Write the three tables describing the corpus, each one whole.

    They are small -- a hundred texts and their authors -- so there is nothing
    to gain from writing them a piece at a time.

    Returns how many rows each file got, e.g.
    {'speakers': 118, 'texts': 104, 'text_authors': 106}
    """
    output_folder = Path(output_folder)

    return {
        'speakers': write_csv(
            output_folder / SPEAKERS_FILE, SPEAKER_COLUMNS, speaker_rows()
        ),
        'texts': write_csv(
            output_folder / TEXTS_FILE, TEXT_COLUMNS, text_rows()
        ),
        'text_authors': write_csv(
            output_folder / TEXT_AUTHORS_FILE, TEXT_AUTHOR_COLUMNS, text_author_rows()
        ),
    }


def export_annotation(text_id, output_folder):
    """Write the sentences and the tokens of one text, two files.

    Returns a summary, e.g.
    {'text_id': 'panov_pechalbari_1936', 'sentences': 2351, 'tokens': 25538}
    """
    output_folder = Path(output_folder)
    file_name = f'{text_id}.csv'

    return {
        'text_id': text_id,
        'sentences': write_csv(
            output_folder / SENTENCES_FOLDER / file_name,
            SENTENCE_COLUMNS,
            sentence_rows(text_id),
        ),
        'tokens': write_csv(
            output_folder / TOKENS_FOLDER / file_name,
            TOKEN_COLUMNS,
            token_rows(text_id),
        ),
    }


def export_everything(output_folder):
    """Write the metadata and every text that has an annotation.

    Returns the metadata summary and one summary per text.
    """
    metadata = export_metadata(output_folder)
    annotations = [
        export_annotation(text_id, output_folder)
        for text_id in annotated_text_ids()
    ]

    return metadata, annotations
