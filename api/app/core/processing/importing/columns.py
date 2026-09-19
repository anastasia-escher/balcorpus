"""The columns of an annotation file, named in one place.

Both the importer and the checks refer to these, so that a column renamed in
the source files has to be changed here and nowhere else.
"""

# Which column identifies what.
TEXT_COLUMN = 'text_id'
SENTENCE_COLUMN = 'sent_id'
TOKEN_COLUMN = 'ud_id'
SPEAKER_COLUMN = 'speaker_id'
TIME_COLUMN = 'time'

# The ud_id of the token's syntactic head inside the same sentence; 0 for the
# root. The editors' spreadsheets called this column "ud_valency", which it
# never was; the cleaned files call it what it is.
HEAD_COLUMN = 'head'

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

# Columns the file cannot be read without.
REQUIRED_COLUMNS = [TEXT_COLUMN, SENTENCE_COLUMN, TOKEN_COLUMN, HEAD_COLUMN]

# Columns that must hold a number, and the parsed value each ends up in.
NUMERIC_CELLS = {
    SENTENCE_COLUMN: 'sentence_number',
    TOKEN_COLUMN: 'ud_id',
    HEAD_COLUMN: 'head_ud_id',
}

# A token without these cannot be placed in the corpus at all.
REQUIRED_NUMBERS = {SENTENCE_COLUMN, TOKEN_COLUMN}
