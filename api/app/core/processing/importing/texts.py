"""Importing the metadata table that describes the corpus documents."""

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug

from core.models import Text

from .cleaning import clean_label, clean_number, clean_text
from .table_reader import read_rows

# The slug that the annotation files also carry, e.g.
# "vasil_iljoski_corbadji_1937".  It is what links the two kinds of file.
TEXT_ID_COLUMN = 'text_id'

# Metadata column -> Text field.  A column missing from the file is simply
# skipped, so an export without "Short Description" still imports.
LABEL_COLUMNS = {
    'Titel': 'text_name',
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


def check_text_id(text_id, row_number):
    """Refuse an identifier that cannot be used to link the files.

    A slug holds letters, digits, hyphens and underscores.  A value with a
    space or a Cyrillic letter in it is almost certainly a title that ended up
    in the wrong column, and it would quietly fail to match any annotation file.
    """
    if not text_id:
        raise ValueError(
            f"Row {row_number} has no {TEXT_ID_COLUMN}. "
            "Every text needs one, because the annotation files refer to it."
        )

    try:
        validate_slug(text_id)
    except ValidationError:
        raise ValueError(
            f"Row {row_number} has the {TEXT_ID_COLUMN} '{text_id}', which is not a "
            "plain identifier.  Expected something like 'vasil_iljoski_corbadji_1937': "
            "latin letters, digits, hyphens and underscores only."
        )


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


def import_texts(path):
    """Create or update one Text per row of the metadata table.

    Returns a summary, e.g. {'created': 2, 'updated': 0}
    """
    created = 0
    updated = 0

    # Row 1 is the heading, so the first row of data is row 2.  Counting from
    # there means an error message points at the line the editor actually sees.
    for row_number, row in enumerate(read_rows(path), start=2):
        text_id = clean_text(row.get(TEXT_ID_COLUMN))
        check_text_id(text_id, row_number)

        fields = build_fields(row)
        # text_name may not be empty, so an untitled text falls back to its id.
        if not fields.get('text_name'):
            fields['text_name'] = text_id

        _, was_created = Text.objects.update_or_create(text_id=text_id, defaults=fields)
        if was_created:
            created += 1
        else:
            updated += 1

    return {'created': created, 'updated': updated}
