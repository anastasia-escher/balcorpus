"""Turning an annotated text into the corpus annotation format.

What changes on the way:

* ``text_id`` held the Macedonian title and ``speaker`` the author's name, so
  neither could be matched against the metadata reliably; both become the
  identifiers the text and speaker tables define;
* the column named ``ud_valency`` never held a valency. It holds the ``ud_id``
  of the token's syntactic head — a preposition depending on the noun at
  position 3 has a 3 there, and every sentence root has a 0 — so it is renamed
  to ``head``;
* the blank rows the source puts between sentences are dropped, since the
  sentence number already says where a sentence ends;
* a first row whose only content is a byte order mark is dropped as well.
"""

from .fields import clean

COLUMNS = [
    'text_id',
    'sent_id',
    'ud_id',
    'source',
    'diplomatic',
    'lemma',
    'ud_pos',
    'pos_tag',
    'pos_ext',
    'head',
    'ud_type',
    'speaker_id',
    'time',
]

# What the column is called in the source, and what it is called here.
RENAMED_COLUMNS = {
    'ud_valency': 'head',
    'speaker': 'speaker_id',
}

# Columns copied across unchanged.
COPIED_COLUMNS = [
    'sent_id', 'ud_id', 'source', 'diplomatic', 'lemma',
    'ud_pos', 'pos_tag', 'pos_ext', 'ud_type', 'time',
]


def is_empty_token(row):
    """True for a row that carries no word at all.

    The first row of several files holds nothing but a byte order mark, which
    the spreadsheet reads as an invisible word. It is not a token.
    """
    return not clean(row.get('source')) and not clean(row.get('lemma'))


def build_token(row, text_id, speaker_id):
    """One row of the source as one row of the annotation file."""
    token = {column: row.get(column) for column in COPIED_COLUMNS}
    token['head'] = row.get('ud_valency')
    token['text_id'] = text_id
    token['speaker_id'] = speaker_id
    return {column: token.get(column) for column in COLUMNS}


def build_annotations(rows, text_id, speaker_id, problems):
    """The whole annotation file, with the identifiers filled in.

    Both identifiers are the same for every row of one file, so they are
    passed in rather than read from each row: that is what makes the file
    point at the metadata instead of repeating it.
    """
    tokens = []
    for number, row in enumerate(rows, start=2):
        if is_empty_token(row):
            problems.append(
                f'annotations row {number}: no word form and no lemma, dropped'
            )
            continue
        tokens.append(build_token(row, text_id, speaker_id))

    return tokens
