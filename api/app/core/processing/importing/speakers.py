"""Importing the metadata table that describes the speakers and authors.

The file is checked completely before anything is written, so a table with
mistakes in it leaves the database exactly as it was.
"""

from django.db import transaction

from core.models import Speaker
from helpers.logger import logger

from .cleaning import clean_gender, clean_label, clean_number, clean_text
from .common_checks import (
    check_duplicate_ids,
    check_identifier,
    check_lengths,
    check_required_columns,
)
from .problems import DataProblems, ProblemList
from .table_reader import read_rows

# The slug the annotation files use in their "speaker" column, e.g.
# "vasil_iljoski".  It is what links a speaker to their tokens.
SPEAKER_ID_COLUMN = 'speaker_id'

# The name the person is known by; for a writer this may be a pen name.
DISPLAY_NAME_COLUMN = 'speaker'

# The name on their papers, which for most people is the same one again.
BIRTH_NAME_COLUMN = 'Full_Name'

GENDER_COLUMN = 'Gender'
BIRTHYEAR_COLUMN = 'Birthyear'

EXAMPLE_SPEAKER_ID = 'vasil_iljoski'

# Metadata column -> Speaker field.
LABEL_COLUMNS = {
    DISPLAY_NAME_COLUMN: 'full_name',
    BIRTH_NAME_COLUMN: 'birth_name',
    'Place_of_Birth': 'place_of_birth',
    'Variety': 'variety',
    'Education': 'education',
    'Religion': 'religion',
    'L1': 'l1',
    'L2': 'l2',
    'L3': 'l3',
}

# Columns the file cannot be read without.
REQUIRED_COLUMNS = [SPEAKER_ID_COLUMN, DISPLAY_NAME_COLUMN]


def build_fields(row):
    """Collect the metadata of one row into keyword arguments for Speaker."""
    fields = {}

    for column, field in LABEL_COLUMNS.items():
        if column in row:
            fields[field] = clean_label(row[column])

    if GENDER_COLUMN in row:
        fields['gender'] = clean_gender(row[GENDER_COLUMN])
    if BIRTHYEAR_COLUMN in row:
        fields['birthyear'] = clean_number(row[BIRTHYEAR_COLUMN])

    # The birth name is only worth storing when it differs from the name the
    # person is known by; otherwise it is the same string twice.
    if fields.get('birth_name') == fields.get('full_name'):
        fields['birth_name'] = None

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
            'record_id': clean_text(row.get(SPEAKER_ID_COLUMN)),
            'typed_birthyear': clean_text(row.get(BIRTHYEAR_COLUMN)),
            'fields': build_fields(row),
        })

    return parsed, column_names


def check_rows(rows, column_names, problems):
    """Look for everything that would make this table impossible to import."""
    check_required_columns(
        column_names, REQUIRED_COLUMNS, problems, 'a table of speaker metadata'
    )
    if problems.has_errors():
        return

    check_duplicate_ids(rows, SPEAKER_ID_COLUMN, problems)
    check_lengths(rows, Speaker, problems)

    for row in rows:
        check_identifier(
            row['record_id'], SPEAKER_ID_COLUMN, row['row_number'],
            problems, EXAMPLE_SPEAKER_ID,
        )
        # A year that cannot be read is worth mentioning but not worth stopping
        # for: the rest of the row is still usable.
        if row['typed_birthyear'] and row['fields'].get('birthyear') is None:
            problems.warning(
                f"{BIRTHYEAR_COLUMN} is '{row['typed_birthyear']}', which is "
                'not a year, so it was left empty',
                row['row_number'],
            )


def write_rows(rows):
    """Create or update one Speaker per row, all of it in one transaction."""
    created = 0
    updated = 0

    with transaction.atomic():
        for row in rows:
            fields = dict(row['fields'])
            # full_name may not be empty, so a nameless row falls back to its
            # identifier.
            if not fields.get('full_name'):
                fields['full_name'] = row['record_id']

            _, was_created = Speaker.objects.update_or_create(
                speaker_id=row['record_id'], defaults=fields
            )
            if was_created:
                created += 1
            else:
                updated += 1

    return {'created': created, 'updated': updated}


def import_speakers(path):
    """Check the speaker table and, if it is clean, import it.

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

    logger.info(f'Writing {len(rows)} speakers')
    return write_rows(rows), problems.warnings
