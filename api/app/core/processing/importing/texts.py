"""Importing the metadata table that describes the corpus documents.

The file is checked completely before anything is written, so a table with
mistakes in it leaves the database exactly as it was.
"""

from django.db import transaction

from core.models import Text
from helpers.logger import logger

from .cleaning import clean_label, clean_number, clean_text
from .common_checks import (
    check_duplicate_ids,
    check_identifier,
    check_lengths,
    check_required_columns,
)
from .problems import DataProblems, ProblemList
from .table_reader import read_rows

# The slug that the annotation files also carry, e.g.
# "vasil_iljoski_corbadji_1937".  It is what links the two kinds of file.
TEXT_ID_COLUMN = 'text_id'
TITLE_COLUMN = 'Titel'

EXAMPLE_TEXT_ID = 'vasil_iljoski_corbadji_1937'

# Metadata column -> Text field.  A column missing from the file is simply
# skipped, so an export without "Short Description" still imports.
LABEL_COLUMNS = {
    TITLE_COLUMN: 'text_name',
    'Data_Genre': 'data_genre',
    'Text_Genre': 'text_genre',
    'Variety': 'variety',
    'Date': 'text_date',
    'Source': 'source',
    'Short Description': 'short_description',
}

# The running number of the editors' own spreadsheet, kept for cross-checking.
NUMBER_COLUMNS = {
    'Text_ID': 'source_number',
}

# Columns the file cannot be read without.
REQUIRED_COLUMNS = [TEXT_ID_COLUMN, TITLE_COLUMN]


def build_fields(row):
    """Collect the metadata of one row into keyword arguments for Text."""
    fields = {}

    for column, field in LABEL_COLUMNS.items():
        if column in row:
            fields[field] = clean_label(row[column])

    for column, field in NUMBER_COLUMNS.items():
        if column in row:
            fields[field] = clean_number(row[column])

    return fields


def parse_rows(path, problems):
    """Read the file, keeping the column names the file actually had.

    Row 1 is the heading, so the first row of data is row 2 and the numbers in
    an error message match what the editor sees in the spreadsheet.
    """
    parsed = []
    column_names = []

    for row_number, row in enumerate(read_rows(path, problems), start=2):
        if not column_names:
            column_names = list(row)

        parsed.append({
            'row_number': row_number,
            'record_id': clean_text(row.get(TEXT_ID_COLUMN)),
            'fields': build_fields(row),
        })

    return parsed, column_names


def check_rows(rows, column_names, problems):
    """Look for everything that would make this table impossible to import."""
    check_required_columns(
        column_names, REQUIRED_COLUMNS, problems, 'a table of text metadata'
    )
    if problems.has_errors():
        return

    check_duplicate_ids(rows, TEXT_ID_COLUMN, problems)
    check_lengths(rows, Text, problems)

    for row in rows:
        check_identifier(
            row['record_id'], TEXT_ID_COLUMN, row['row_number'],
            problems, EXAMPLE_TEXT_ID,
        )
        if not row['fields'].get('text_name'):
            problems.warning(
                f'{TITLE_COLUMN} is empty, so the identifier will be shown as '
                'the title',
                row['row_number'],
            )


def write_rows(rows):
    """Create or update one Text per row, all of it in one transaction."""
    created = 0
    updated = 0

    with transaction.atomic():
        for row in rows:
            fields = dict(row['fields'])
            # text_name may not be empty, so an untitled text falls back to its
            # identifier.
            if not fields.get('text_name'):
                fields['text_name'] = row['record_id']

            _, was_created = Text.objects.update_or_create(
                text_id=row['record_id'], defaults=fields
            )
            if was_created:
                created += 1
            else:
                updated += 1

    return {'created': created, 'updated': updated}


def import_texts(path):
    """Check the metadata table and, if it is clean, import it.

    Raises DataProblems when the table has errors; the database is then left
    untouched.  Returns the summary and the warnings worth showing anyway.
    """
    problems = ProblemList()

    logger.info(f'Reading {path}')
    rows, column_names = parse_rows(path, problems)
    logger.info(f'{len(rows)} rows read')

    # A file whose columns have shifted makes every later check meaningless,
    # so it is reported on its own.
    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    logger.info('Checking the metadata before writing anything')
    check_rows(rows, column_names, problems)
    if problems.has_errors():
        raise DataProblems(path, problems.errors, problems.warnings)

    logger.info(f'Writing {len(rows)} texts')
    return write_rows(rows), problems.warnings
