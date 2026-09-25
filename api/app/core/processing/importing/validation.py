"""Checking annotation rows before any of them reaches the database.

Every function here takes the rows that were read from the file and a
ProblemList to write its findings into.  None of them raises: the point is to
gather the complete picture of what is wrong with the file.

A row looks like this:
    {'row_number': 5, 'sentence_number': 2, 'speaker_slug': 'vasil_iljoski',
     'fields': {'ud_id': 1, 'source': 'Васил', 'head_ud_id': 0, ...}}
"""

from collections import defaultdict

from core.models import Token

from .columns import NUMERIC_CELLS, REQUIRED_NUMBERS

# The root of a sentence has no head, which UD writes as head 0.
ROOT_HEAD = 0

def max_lengths():
    """How long each text column of Token may be, read from the model itself.

    Asking the model means the numbers cannot drift apart from the migration.
    """
    lengths = {}
    for field in Token._meta.get_fields():
        if getattr(field, 'max_length', None):
            lengths[field.name] = field.max_length

    return lengths


def check_numeric_cells(row, problems):
    """Complain about a cell that should hold a number but does not.

    A cell that was simply left empty gets a different message from one that
    holds something like "икс", because they are different mistakes.
    """
    for column, parsed_name in NUMERIC_CELLS.items():
        typed = row['raw_numbers'][column]
        parsed = row['fields'].get(parsed_name, row.get(parsed_name))

        if parsed is not None:
            continue

        if typed:
            problems.error(f"{column} is '{typed}', which is not a number", row['row_number'])
        elif column in REQUIRED_NUMBERS:
            problems.error(f'{column} is empty', row['row_number'])
        else:
            problems.warning(f'{column} is empty, so the token has no head', row['row_number'])


def check_duplicate_tokens(rows, problems):
    """Two rows may not describe the same token of the same sentence."""
    first_seen = {}

    for row in rows:
        key = (row['sentence_number'], row['fields']['ud_id'])
        if None in key:
            continue

        if key in first_seen:
            problems.error(
                f"sent_id {key[0]} / ud_id {key[1]} was already used in row "
                f"{first_seen[key]}",
                row['row_number'],
            )
        else:
            first_seen[key] = row['row_number']


def check_heads(rows, problems):
    """Every head must point at a token that exists in the same sentence."""
    token_ids_of_sentence = defaultdict(set)
    for row in rows:
        token_ids_of_sentence[row['sentence_number']].add(row['fields']['ud_id'])

    for row in rows:
        head = row['fields']['head_ud_id']
        if head is None or head == ROOT_HEAD:
            continue

        if head not in token_ids_of_sentence[row['sentence_number']]:
            problems.error(
                f"the head {head} does not exist in sentence "
                f"{row['sentence_number']}",
                row['row_number'],
            )


def check_roots(rows, problems):
    """Warn about sentences that do not have exactly one root.

    Universal Dependencies asks for exactly one, but half-annotated material
    happens, so this is a warning rather than a reason to stop.
    """
    roots_of_sentence = defaultdict(int)
    first_row_of_sentence = {}

    for row in rows:
        sentence = row['sentence_number']
        first_row_of_sentence.setdefault(sentence, row['row_number'])
        if row['fields']['head_ud_id'] == ROOT_HEAD:
            roots_of_sentence[sentence] += 1

    for sentence, first_row in first_row_of_sentence.items():
        count = roots_of_sentence[sentence]
        if count == 1:
            continue

        found = 'no root' if count == 0 else f'{count} roots'
        problems.warning(f'sentence {sentence} has {found}', first_row)


def check_lengths(rows, problems):
    """Refuse values that would not fit into their database column."""
    lengths = max_lengths()

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


def check_speakers(rows, known_speaker_slugs, problems, allow_unknown):
    """Every speaker named in the file should exist in the speaker table.

    With ``allow_unknown`` the missing ones are only reported, and their
    sentences end up without a speaker.
    """
    first_row_of_slug = {}
    for row in rows:
        slug = row['speaker_slug']
        if slug and slug not in known_speaker_slugs:
            first_row_of_slug.setdefault(slug, row['row_number'])

    for slug, row_number in first_row_of_slug.items():
        message = (
            f"no speaker has the speaker_id or the name '{slug}'. Import the "
            "speaker table first, or pass --allow-unknown-speakers to import anyway"
        )
        if allow_unknown:
            problems.warning(message, row_number)
        else:
            problems.error(message, row_number)


def check_annotation_rows(rows, known_speaker_slugs, problems, allow_unknown_speakers):
    """Run every check over the rows of one annotation file."""
    for row in rows:
        check_numeric_cells(row, problems)

    check_duplicate_tokens(rows, problems)
    check_heads(rows, problems)
    check_roots(rows, problems)
    check_lengths(rows, problems)
    check_speakers(rows, known_speaker_slugs, problems, allow_unknown_speakers)
