"""Checks every importer needs, whatever kind of file it is reading.

Like the checks in validation.py, none of these raises: each one writes what it
found into a ProblemList, so that one run reports everything wrong with a file.

They all expect rows of the shape
    {'row_number': 5, 'record_id': 'panov_anton', 'fields': {...}}
"""

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug


def max_lengths(model):
    """How long each text column of a model may be, read from the model itself.

    Asking the model means the numbers cannot drift apart from the migrations.

    Example: max_lengths(Token) -> {'source': 255, 'pos_tag': 50, ...}
    """
    lengths = {}
    for field in model._meta.get_fields():
        if getattr(field, 'max_length', None):
            lengths[field.name] = field.max_length

    return lengths


def check_lengths(rows, model, problems):
    """Refuse values that would not fit into their database column."""
    lengths = max_lengths(model)

    for row in rows:
        for name, value in row['fields'].items():
            limit = lengths.get(name)
            if limit is None or value is None:
                continue

            if len(str(value)) > limit:
                problems.error(
                    f"{name} is {len(str(value))} characters long, but at most "
                    f"{limit} fit: {str(value)[:40]}...",
                    row['row_number'],
                )


def check_required_columns(column_names, required_columns, problems, expected):
    """Make sure the file is the kind of file we were expecting.

    A workbook where the wrong sheet was exported has none of the columns, and
    saying so is far more useful than a hundred empty-value errors.
    """
    if not column_names:
        problems.error('the file has no data rows')
        return

    missing = [column for column in required_columns if column not in column_names]
    if missing:
        problems.error(
            'these columns are missing: ' + ', '.join(missing)
            + f'. Expected {expected} with the columns '
            + ', '.join(required_columns) + '.'
        )


def check_duplicate_ids(rows, id_column, problems):
    """Two rows of one file may not describe the same thing.

    Without this the second row would quietly overwrite the first, and nobody
    would find out which of the two versions ended up in the corpus.
    """
    first_seen = {}

    for row in rows:
        record_id = row['record_id']
        if not record_id:
            continue

        if record_id in first_seen:
            problems.error(
                f"{id_column} '{record_id}' was already used in row "
                f"{first_seen[record_id]}",
                row['row_number'],
            )
        else:
            first_seen[record_id] = row['row_number']


def check_identifier(record_id, id_column, row_number, problems, example):
    """Refuse an identifier that cannot be used to link the files.

    An identifier holds latin letters, digits, hyphens and underscores.  A value
    with a space or a Cyrillic letter in it is almost certainly a title or a
    name that ended up in the wrong column, and it would quietly fail to match
    anything.
    """
    if not record_id:
        problems.error(
            f'{id_column} is missing. It is what the other files refer to, '
            f"so every row needs one, e.g. '{example}'.",
            row_number,
        )
        return

    try:
        validate_slug(record_id)
    except ValidationError:
        problems.error(
            f"{id_column} is '{record_id}', which is not a plain identifier. "
            f"Expected something like '{example}': latin letters, digits, "
            'hyphens and underscores only.',
            row_number,
        )
