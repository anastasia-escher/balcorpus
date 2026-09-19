"""What each column of the data set means.

This is the single description of the data: the machine-readable
``datapackage.json`` that ships with the files and the ``README.md`` a person
reads are both generated from it, so the two cannot drift apart.

The shape follows the Frictionless Data Table Schema, which is what most
tools expect a documented data set to look like.
"""

from .vocabularies import (
    DATA_GENRE,
    DIALECT_REGION,
    EDUCATION_LEVEL,
    LANGUAGE,
    RELIGION,
    SEX,
    TEXT_GENRE,
    TEXT_VARIETY,
)


def field(name, field_type, description, **extra):
    """One column of a table."""
    return {'name': name, 'type': field_type, 'description': description, **extra}


def values_of(vocabulary):
    """The distinct English values a vocabulary produces, in order."""
    seen = []
    for value in vocabulary.values():
        if value not in seen:
            seen.append(value)
    return seen


SPEAKERS = {
    'name': 'speakers',
    'path': 'speakers.xlsx',
    'title': 'Speakers and authors',
    'description': 'One row per person whose language the corpus records.',
    'primaryKey': 'speaker_id',
    'fields': [
        field('speaker_id', 'string',
              'Identifier used by texts.xlsx and by the annotation files.',
              example='anton_panov'),
        field('name', 'string',
              'The name the person is known by, in Macedonian Cyrillic. For a '
              'writer this may be a pen name.'),
        field('birth_name', 'string',
              'The name on their papers, filled in only when it differs from '
              'name.'),
        field('sex', 'string', 'Recorded sex of the speaker.',
              enum=values_of(SEX)),
        field('birth_year', 'year', 'Year of birth.'),
        field('place_of_birth', 'string',
              'Settlement of birth, romanised. A second name the settlement '
              'goes by is kept in brackets.'),
        field('place_type', 'string', 'Whether that settlement is a village or a town.',
              enum=['village', 'town']),
        field('municipality', 'string',
              'Municipality the settlement belongs to, romanised, when the '
              'source named one.'),
        field('dialect_region', 'string',
              'Dialect area the speaker comes from. Areas inside Macedonia are '
              'compass directions; speakers from elsewhere are given by country, '
              'with a part of it in brackets.',
              enum=values_of(DIALECT_REGION)),
        field('education_level', 'string', 'How far the speaker went in school.',
              enum=values_of(EDUCATION_LEVEL)),
        field('education_note', 'string',
              'What kind of school, when the source said so.'),
        field('religion', 'string', 'Recorded religion.', enum=values_of(RELIGION)),
        field('l1', 'string', 'First language, as ISO 639-1 codes.',
              example='mk'),
        field('l2', 'string',
              'Second language. Several codes are separated by a semicolon.',
              example='sr;hr'),
        field('l3', 'string', 'Third language, written like l2.'),
        field('notes', 'string',
              'Remarks the source hid inside cells that were meant to hold a '
              'value, such as postings as an ambassador.'),
        field('source_row', 'integer',
              'Row number in the spreadsheet this came from, for checking '
              'against the editors’ own copy.'),
    ],
}

TEXTS = {
    'name': 'texts',
    'path': 'texts.xlsx',
    'title': 'Texts',
    'description': 'One row per document of the corpus.',
    'primaryKey': 'text_id',
    'foreignKeys': [
        {'fields': 'author_id',
         'reference': {'resource': 'speakers', 'fields': 'speaker_id'}},
    ],
    'fields': [
        field('text_id', 'string',
              'Identifier used by the annotation files: author surname, short '
              'title, year.',
              example='panov_pechalbari_1936'),
        field('title', 'string', 'Title of the text, in Macedonian Cyrillic.'),
        field('author_id', 'string', 'The author, as a speaker_id.'),
        field('data_genre', 'string', 'What kind of material this is.',
              enum=values_of(DATA_GENRE)),
        field('text_genre', 'string',
              'Literary genre. Several genres are separated by a semicolon.',
              enum=values_of(TEXT_GENRE), example='drama;prose'),
        field('variety', 'string',
              'Whether the text is in the standard language or a dialect.',
              enum=values_of(TEXT_VARIETY)),
        field('variety_note', 'string',
              'What the source wrote beside the variety, romanised: which '
              'dialect, or why both are named.'),
        field('year', 'year', 'Year of publication. The first one, if several.'),
        field('year_note', 'string',
              'Further years the source gave, for a text published more than once.'),
        field('source_url', 'string', 'Where the text can be read online.'),
        field('source_file', 'string',
              'Name of the file the editors delivered, kept as the record of '
              'where this row came from.'),
        field('source_row', 'integer',
              'Row number in the spreadsheet this came from.'),
    ],
}

ANNOTATIONS = {
    'name': 'annotations',
    'path': 'annotations/*.xlsx',
    'title': 'Annotated texts',
    'description': (
        'One file per text, one row per token, in the order of the text. '
        'Morphology follows MULTEXT-East, syntax follows Universal Dependencies.'
    ),
    'primaryKey': ['text_id', 'sent_id', 'ud_id'],
    'foreignKeys': [
        {'fields': 'text_id',
         'reference': {'resource': 'texts', 'fields': 'text_id'}},
        {'fields': 'speaker_id',
         'reference': {'resource': 'speakers', 'fields': 'speaker_id'}},
    ],
    'fields': [
        field('text_id', 'string', 'The text this token belongs to.'),
        field('sent_id', 'integer', 'Number of the sentence within the text.'),
        field('ud_id', 'integer', 'Position of the token within the sentence.'),
        field('source', 'string', 'The word form as it stands in the text.'),
        field('diplomatic', 'string',
              'The word form in diplomatic transcription, where the corpus has one.'),
        field('lemma', 'string', 'Dictionary form of the word.'),
        field('ud_pos', 'string', 'Universal part-of-speech tag.', example='NOUN'),
        field('pos_tag', 'string', 'MULTEXT-East morphosyntactic description.',
              example='Ncmsnn'),
        field('pos_ext', 'string', 'Universal Dependencies features.',
              example='Case=Nom|Gender=Masc|Number=Sing'),
        field('head', 'integer',
              'The ud_id of this token’s syntactic head in the same sentence. '
              '0 means the token is the root. The source called this column '
              'ud_valency, which it never was.'),
        field('ud_type', 'string',
              'Universal Dependencies relation to the head, subtypes included.',
              example='nsubj:pass'),
        field('speaker_id', 'string', 'Who produced this stretch of language.'),
        field('time', 'string',
              'Timecode in the recording; only spoken material has one.'),
    ],
}

RESOURCES = [SPEAKERS, TEXTS, ANNOTATIONS]

# The types the schema calls numbers. The Excel writer uses this so that a
# year is a year in the spreadsheet and not a string that looks like one.
NUMERIC_TYPES = {'integer', 'year'}


def numeric_columns(resource):
    """The columns of one resource that hold numbers.

    Example: numeric_columns(TEXTS) -> {'year', 'source_row'}
    """
    return {
        entry['name']
        for entry in resource['fields']
        if entry['type'] in NUMERIC_TYPES
    }

LANGUAGE_CODES = values_of(LANGUAGE)
