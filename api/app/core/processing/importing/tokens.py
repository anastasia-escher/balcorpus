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

    Row 1 of the file is the heading, so the first row of data is row 2 and the
    numbers in an error message match what the linguist sees in Excel.
    """
    parsed = []
    column_names = []

    for row_number, row in enumerate(read_rows(path, problems), start=2):
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


def check_columns(column_names, problems):
    """Make sure the file is the kind of file we were expecting.

    A workbook where the wrong sheet was exported has none of these columns,
    and saying so is far more useful than a hundred empty-value errors.
    """
    if not column_names:
        problems.error('the file has no data rows')
        return

    missing = [column for column in REQUIRED_COLUMNS if column not in column_names]
    if missing:
        problems.error(
            'these columns are missing: ' + ', '.join(missing)
            + '. Expected an annotation file with the columns '
            + ', '.join(REQUIRED_COLUMNS) + '.'
        )


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
            f"the text '{text_id}' is not in the database. Import the metadata "
            'table first: manage.py import_texts <file>.'
        )


def group_rows_by_text(rows):
    """Sort the rows into one bucket per text.

    A file normally holds a single text, but nothing stops it from holding
    several, so the grouping is done anyway.
    """
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['text_id']].append(row)

    return grouped


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


def import_tokens(path, allow_unknown_speakers=False):
    """Check an annotation file and, if it is clean, import it.

    Raises DataProblems when the file has errors; in that case the database is
    left untouched.  Returns one summary per text found in the file, and the
    warnings worth showing even for a file that went through.
    """
    problems = ProblemList()

    logger.info(f'Reading {path}')
    rows, column_names = parse_rows(path, problems)

    check_columns(column_names, problems)
    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    sentence_count = len({row['sentence_number'] for row in rows})
    logger.info(f'{len(rows)} rows read, {sentence_count} sentences')

    # A file whose columns have shifted makes every later check meaningless,
    # so it is reported on its own.
    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    logger.info('Checking the annotation before writing anything')
    known_speaker_slugs = set(Speaker.objects.values_list('speaker_id', flat=True))
    check_annotation_rows(rows, known_speaker_slugs, problems, allow_unknown_speakers)
    check_texts_exist(rows, problems)

    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    summaries = []
    for text_id, text_rows in group_rows_by_text(rows).items():
        text = Text.objects.get(text_id=text_id)
        logger.info(f'Writing {len(text_rows)} tokens for {text_id}')
        summaries.append(write_text_rows(text, text_rows))

    return summaries, problems.warnings
