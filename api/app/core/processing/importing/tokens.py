"""Importing an annotation file into sentences and tokens.

Re-importing a file replaces everything the corpus holds for that text, so
running the command twice leaves the same result as running it once.
"""

from collections import defaultdict

from core.models import Sentence, Speaker, Text, Token

from .cleaning import clean_annotation, clean_number, clean_text
from .table_reader import read_rows

# Which column identifies what.
TEXT_COLUMN = 'text_id'
SENTENCE_COLUMN = 'sent_id'
TOKEN_COLUMN = 'ud_id'
SPEAKER_COLUMN = 'speaker'

# The column named "ud_valency" holds the ud_id of the token's syntactic head,
# not a valency: a preposition depending on the noun at position 3 has a 3
# there, and every sentence root has a 0.
HEAD_COLUMN = 'ud_valency'

# Columns holding the source material itself.  These are only trimmed, never
# otherwise altered.
SOURCE_COLUMNS = {
    'source': 'source',
    'diplomatic': 'diplomatic',
    'lemma': 'lemma',
}

# Columns holding annotation, where a lone "_" means "no value".
ANNOTATION_COLUMNS = {
    'ud_pos': 'ud_pos',
    'pos_tag': 'pos_tag',
    'pos_ext': 'pos_ext',
    'ud_type': 'ud_type',
}

TIME_COLUMN = 'time'

# How many rows go to the database in one statement.  Inserting the tokens one
# by one would mean tens of thousands of round trips for a single file.
BATCH_SIZE = 1000


def build_token_fields(row):
    """Read one row into keyword arguments for Token.

    Example: {'ud_id': 2, 'source': 'молим', 'lemma': 'молим',
              'ud_pos': 'INTJ', 'head_ud_id': 0, 'ud_type': 'root', ...}
    """
    fields = {
        'ud_id': clean_number(row.get(TOKEN_COLUMN)),
        'head_ud_id': clean_number(row.get(HEAD_COLUMN)),
        'time': clean_text(row.get(TIME_COLUMN)),
    }

    for column, field in SOURCE_COLUMNS.items():
        fields[field] = clean_text(row.get(column))

    for column, field in ANNOTATION_COLUMNS.items():
        fields[field] = clean_annotation(row.get(column))

    return fields


def group_rows_by_text(rows):
    """Sort the rows of a file into one bucket per text.

    A file normally holds a single text, but nothing stops it from holding
    several, so the grouping is done anyway.
    """
    grouped = defaultdict(list)
    for row in rows:
        text_id = clean_text(row.get(TEXT_COLUMN))
        grouped[text_id].append(row)

    return grouped


def find_text(text_id, path):
    """Look up the text this file belongs to, or explain why it is missing."""
    if not text_id:
        raise ValueError(
            f"{path} has rows without a {TEXT_COLUMN}. Every row must name the "
            "text it belongs to, e.g. 'vasil_iljoski_corbadji_1937'."
        )

    text = Text.objects.filter(text_id=text_id).first()
    if text is None:
        raise ValueError(
            f"{path} refers to the text '{text_id}', which is not in the database. "
            "Import the metadata table first: manage.py import_texts <file>."
        )

    return text


def import_text_rows(text, rows):
    """Replace everything stored for one text with the rows of this file.

    Returns a summary, e.g.
    {'text_id': 'vasil_iljoski_corbadji_1937', 'sentences': 2351,
     'tokens': 25538, 'replaced_sentences': 0, 'unknown_speakers': []}
    """
    speakers_by_slug = {speaker.speaker_id: speaker for speaker in Speaker.objects.all()}
    unknown_speakers = set()

    # Sentence numbers in the order they appear, so the corpus keeps the order
    # of the original document rather than the order of a database scan.
    sentence_numbers = []
    speaker_of_sentence = {}
    token_fields_of_sentence = defaultdict(list)

    for row in rows:
        sentence_number = clean_number(row.get(SENTENCE_COLUMN))
        token_fields = build_token_fields(row)
        if sentence_number is None or token_fields['ud_id'] is None:
            continue

        if sentence_number not in token_fields_of_sentence:
            sentence_numbers.append(sentence_number)

        token_fields_of_sentence[sentence_number].append(token_fields)

        speaker_slug = clean_text(row.get(SPEAKER_COLUMN))
        if speaker_slug and sentence_number not in speaker_of_sentence:
            speaker = speakers_by_slug.get(speaker_slug)
            if speaker is None:
                unknown_speakers.add(speaker_slug)
            else:
                speaker_of_sentence[sentence_number] = speaker

    replaced = Sentence.objects.filter(text=text).count()
    Sentence.objects.filter(text=text).delete()

    sentences = [
        Sentence(
            text=text,
            sentence_id=number,
            speaker=speaker_of_sentence.get(number),
        )
        for number in sentence_numbers
    ]
    Sentence.objects.bulk_create(sentences, batch_size=BATCH_SIZE)

    tokens = [
        Token(sentence=sentence, **fields)
        for sentence in sentences
        for fields in token_fields_of_sentence[sentence.sentence_id]
    ]
    Token.objects.bulk_create(tokens, batch_size=BATCH_SIZE)

    # The speakers appearing in a text are part of its metadata, so the link is
    # recorded on the text as well; that is what lets a speaker page list the
    # texts they appear in.
    text.authors.set(set(speaker_of_sentence.values()))

    return {
        'text_id': text.text_id,
        'sentences': len(sentences),
        'tokens': len(tokens),
        'replaced_sentences': replaced,
        'unknown_speakers': sorted(unknown_speakers),
    }


def import_tokens(path):
    """Import every text contained in one annotation file.

    Returns one summary per text found in the file.
    """
    grouped = group_rows_by_text(read_rows(path))

    summaries = []
    for text_id, rows in grouped.items():
        text = find_text(text_id, path)
        summaries.append(import_text_rows(text, rows))

    return summaries
