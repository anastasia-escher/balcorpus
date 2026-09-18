"""Importing the metadata table that describes the speakers and authors."""

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug

from core.models import Speaker

from .cleaning import clean_gender, clean_label, clean_number, clean_text
from .table_reader import read_rows

# The slug the annotation files use in their "speaker" column, e.g.
# "vasil_iljoski".  It is what links a speaker to their tokens.
SPEAKER_ID_COLUMN = 'speaker_id'

# The name the person is known by; for a writer this may be a pen name.
DISPLAY_NAME_COLUMN = 'speaker'

# Metadata column -> Speaker field.
LABEL_COLUMNS = {
    DISPLAY_NAME_COLUMN: 'full_name',
    'Full_Name': 'birth_name',
    'Place_of_Birth': 'place_of_birth',
    'Variety': 'variety',
    'Education': 'education',
    'Religion': 'religion',
    'L1': 'l1',
    'L2': 'l2',
    'L3': 'l3',
}


def check_speaker_id(speaker_id, row_number):
    """Refuse an identifier that cannot be used to link the files."""
    if not speaker_id:
        raise ValueError(
            f"Row {row_number} has no {SPEAKER_ID_COLUMN}. "
            "Every speaker needs one, because the annotation files refer to it. "
            f"Expected a column '{SPEAKER_ID_COLUMN}' holding values like 'vasil_iljoski'."
        )

    try:
        validate_slug(speaker_id)
    except ValidationError:
        raise ValueError(
            f"Row {row_number} has the {SPEAKER_ID_COLUMN} '{speaker_id}', which is not "
            "a plain identifier.  Expected something like 'vasil_iljoski': latin "
            "letters, digits, hyphens and underscores only."
        )


def build_fields(row):
    """Collect the metadata of one row into keyword arguments for Speaker."""
    fields = {}

    for column, field in LABEL_COLUMNS.items():
        if column in row:
            fields[field] = clean_label(row[column])

    if 'Gender' in row:
        fields['gender'] = clean_gender(row['Gender'])
    if 'Birthyear' in row:
        fields['birthyear'] = clean_number(row['Birthyear'])

    # The birth name is only worth storing when it differs from the name the
    # person is known by; otherwise it is the same string twice.
    if fields.get('birth_name') == fields.get('full_name'):
        fields['birth_name'] = None

    return fields


def import_speakers(path):
    """Create or update one Speaker per row of the metadata table.

    Returns a summary, e.g. {'created': 10, 'updated': 0}
    """
    created = 0
    updated = 0

    # Row 1 is the heading, so the first row of data is row 2.
    for row_number, row in enumerate(read_rows(path), start=2):
        speaker_id = clean_text(row.get(SPEAKER_ID_COLUMN))
        check_speaker_id(speaker_id, row_number)

        fields = build_fields(row)
        # full_name may not be empty, so a nameless row falls back to its id.
        if not fields.get('full_name'):
            fields['full_name'] = speaker_id

        _, was_created = Speaker.objects.update_or_create(
            speaker_id=speaker_id, defaults=fields
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {'created': created, 'updated': updated}
