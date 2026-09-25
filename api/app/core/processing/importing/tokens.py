"""Importing an annotation file into sentences and tokens.

The file is read and checked completely before anything is written.  If it has
errors, nothing at all reaches the database and the caller gets the full list,
so the linguists can correct the file in one go.

Re-importing a clean file replaces everything the corpus holds for that text,
so running the command twice leaves the same result as running it once.
"""

from collections import defaultdict

from django.db import transaction

from core.models import Sentence, Speaker, Text, Token
from helpers.logger import logger

from .cleaning import clean_annotation, clean_number, clean_text
from .columns import (
    ANNOTATION_COLUMNS,
    HEAD_COLUMN,
    REQUIRED_COLUMNS,
    SENTENCE_COLUMN,
    SOURCE_COLUMNS,
    SPEAKER_COLUMN,
    TEXT_COLUMN,
    TIME_COLUMN,
    TOKEN_COLUMN,
)
from .common_checks import check_required_columns
from .linguist_format import (
    drop_rows_without_a_word,
    find_speaker_ids,
    find_text_ids,
    use_corpus_column_names,
)
from .problems import DataProblems, ProblemList
from .table_reader import read_rows
from .validation import check_annotation_rows

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


def parse_rows(path, problems):
    """Read the file into rows that the checks and the writing both understand.

    Returns the rows together with the column names the file actually had, so
    the file only has to be opened once.

    Each row keeps the number Excel shows for it, so an error message points
    at the line the linguist sees.
    """
    parsed = []
    column_names = []

    for row_number, row in read_rows(path, problems):
        row = use_corpus_column_names(row)
        if not column_names:
            column_names = list(row)

        parsed.append({
            'row_number': row_number,
            'sentence_number': clean_number(row.get(SENTENCE_COLUMN)),
            'speaker_slug': clean_text(row.get(SPEAKER_COLUMN)),
            'text_id': clean_text(row.get(TEXT_COLUMN)),
            # The cells as they were typed, so a value that is not a number can
            # be told apart from a cell that was simply left empty.
            'raw_numbers': {
                SENTENCE_COLUMN: clean_text(row.get(SENTENCE_COLUMN)),
                TOKEN_COLUMN: clean_text(row.get(TOKEN_COLUMN)),
                HEAD_COLUMN: clean_text(row.get(HEAD_COLUMN)),
            },
            'fields': build_token_fields(row),
        })

    return parsed, column_names


def check_texts_exist(rows, problems):
    """Every text named in the file must already be in the database."""
    named_texts = {row['text_id'] for row in rows}

    if None in named_texts:
        problems.error(
            f'some rows have no {TEXT_COLUMN}. Every row must name the text it '
            "belongs to, e.g. 'vasil_iljoski_corbadji_1937'."
        )
        named_texts.discard(None)

    known = set(Text.objects.filter(text_id__in=named_texts).values_list('text_id', flat=True))
    for text_id in sorted(named_texts - known):
        problems.error(
            f"no text has the text_id or the title '{text_id}'. Add the text to "
            'the metadata table and import it first (manage.py import_texts '
            '<file>), or name it with --text.'
        )


def check_one_text(rows, problems):
    """A file must hold exactly one text.

    That is how the linguists deliver them, and every check here counts
    sentences within the file: with two texts, sentence 1 of each would look
    like the same sentence written twice.
    """
    named_texts = {row['text_id'] for row in rows if row['text_id']}

    if not named_texts:
        problems.error('the file has no tokens')
    elif len(named_texts) > 1:
        problems.error(
            'the file holds more than one text: ' + ', '.join(sorted(named_texts))
            + '. Please send each text as a file of its own.'
        )


def write_text_rows(text, rows):
    """Replace everything stored for one text with the rows of this file.

    Everything happens in one transaction: if any part of it fails, the text
    keeps the data it had before, rather than being left half emptied.

    The text's authors are not touched here. Who wrote a text is metadata and
    comes from the text table; who speaks in it is recorded on each sentence.

    Returns a summary, e.g.
    {'text_id': 'vasil_iljoski_corbadji_1937', 'sentences': 2351,
     'tokens': 25538, 'replaced_sentences': 0}
    """
    speakers_by_slug = {speaker.speaker_id: speaker for speaker in Speaker.objects.all()}

    # Sentence numbers in the order they appear, so the corpus keeps the order
    # of the original document rather than the order of a database scan.
    sentence_numbers = []
    speaker_of_sentence = {}
    token_fields_of_sentence = defaultdict(list)

    for row in rows:
        number = row['sentence_number']
        if number not in token_fields_of_sentence:
            sentence_numbers.append(number)

        token_fields_of_sentence[number].append(row['fields'])

        slug = row['speaker_slug']
        if slug and number not in speaker_of_sentence and slug in speakers_by_slug:
            speaker_of_sentence[number] = speakers_by_slug[slug]

    with transaction.atomic():
        replaced = Sentence.objects.filter(text=text).count()
        if replaced:
            logger.info(f'Replacing the {replaced} sentences already stored for {text.text_id}')
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

    return {
        'text_id': text.text_id,
        'sentences': len(sentences),
        'tokens': len(tokens),
        'replaced_sentences': replaced,
    }


def import_tokens(path, allow_unknown_speakers=False, text_id=None):
    """Check an annotation file and, if it is clean, import it.

    The file may be in the corpus format or exactly as the linguists send it
    (see linguist_format). ``text_id`` names the text for every row, for a
    file whose title belongs to more than one text.

    Raises DataProblems when the file has errors; in that case the database is
    left untouched.  Returns the summary of the text, and the warnings worth
    showing even for a file that went through.
    """
    problems = ProblemList()

    logger.info(f'Reading {path}')
    rows, column_names = parse_rows(path, problems)

    # A file whose columns have shifted makes every later check meaningless,
    # so it is reported on its own.
    check_required_columns(column_names, REQUIRED_COLUMNS, problems, 'an annotation file')
    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    rows = drop_rows_without_a_word(rows, problems)
    find_text_ids(rows, text_id, problems)
    find_speaker_ids(rows, problems)

    sentence_count = len({row['sentence_number'] for row in rows})
    logger.info(f'{len(rows)} rows read, {sentence_count} sentences')

    logger.info('Checking the annotation before writing anything')
    check_one_text(rows, problems)
    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    known_speaker_slugs = set(Speaker.objects.values_list('speaker_id', flat=True))
    check_annotation_rows(rows, known_speaker_slugs, problems, allow_unknown_speakers)
    check_texts_exist(rows, problems)

    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    text = Text.objects.get(text_id=rows[0]['text_id'])
    logger.info(f'Writing {len(rows)} tokens for {text.text_id}')
    summary = write_text_rows(text, rows)

    return summary, problems.warnings
