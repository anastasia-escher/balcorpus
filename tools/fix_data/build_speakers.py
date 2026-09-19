"""Turning the speaker spreadsheet into the corpus speaker table.

What changes on the way:

* every speaker gets a stable identifier, ``anton_panov``, which the texts and
  the annotation files use to refer to them;
* ``speaker`` and ``Full_Name`` hold the same string in all but one row, so
  the birth name is only kept when it actually differs;
* the place of birth is split into settlement, kind and municipality;
* levels, regions, religion and languages become the English vocabularies;
* remarks that the source hid inside "NA (...)" cells move to ``notes``.
"""

from .fields import (
    Unknown,
    clean,
    read_education,
    read_languages,
    read_region,
    translate_remark,
)
from .places import split_place
from .slugs import speaker_slug
from .vocabularies import RELIGION, SEX

COLUMNS = [
    'speaker_id',
    'name',
    'birth_name',
    'sex',
    'birth_year',
    'place_of_birth',
    'place_type',
    'municipality',
    'dialect_region',
    'education_level',
    'education_note',
    'religion',
    'l1',
    'l2',
    'l3',
    'notes',
    'source_row',
]

LANGUAGE_COLUMNS = ['L1', 'L2', 'L3']


def collect(value, problems, row_number):
    """Keep a translated value, or record it as untranslated and drop it."""
    if isinstance(value, Unknown):
        problems.append(f'speakers row {row_number}: no translation for {value}')
        return None

    return value


def join(values):
    """Several codes in one cell, as the data dictionary describes them."""
    return ';'.join(value for value in values if value)


def build_speaker(row, row_number, problems):
    """One row of the source as one row of the speaker table."""
    name = clean(row.get('speaker')) or clean(row.get('Full_Name'))
    birth_name = clean(row.get('Full_Name'))
    settlement, place_type, municipality = split_place(clean(row.get('Place_of_Birth')))
    level, education_note = read_education(clean(row.get('Education')))

    languages = {}
    remarks = []
    for column in LANGUAGE_COLUMNS:
        codes, remark = read_languages(clean(row.get(column)), column)
        languages[column] = join(collect(code, problems, row_number) for code in codes)
        if remark:
            remarks.append(remark)

    religion = read_religion(clean(row.get('Religion')), remarks)

    return {
        'speaker_id': speaker_slug(name),
        'name': name,
        # Only worth storing when the person is known by a different name.
        'birth_name': birth_name if birth_name and birth_name != name else '',
        'sex': collect(read_sex(clean(row.get('Gender'))), problems, row_number) or '',
        'birth_year': clean(row.get('Birthyear')) or '',
        'place_of_birth': settlement or '',
        'place_type': place_type or '',
        'municipality': municipality or '',
        'dialect_region': collect(read_region(clean(row.get('Variety'))), problems, row_number) or '',
        'education_level': collect(level, problems, row_number) or '',
        'education_note': education_note or '',
        'religion': religion or '',
        'l1': languages['L1'],
        'l2': languages['L2'],
        'l3': languages['L3'],
        'notes': '; '.join(remarks),
        'source_row': row.get('ID') or '',
    }


def read_sex(value):
    """The sex of the speaker, or an Unknown when the cell says something else."""
    if value is None:
        return None

    return SEX.get(value, Unknown('Gender', value))


def read_religion(value, remarks):
    """Read a religion cell, moving what it cannot name into the remarks.

    The source writes "NA, веројатно муслиман" — no religion recorded, plus a
    remark about it. The remark is worth keeping; it is just not a religion.
    """
    if value is None:
        return None

    if value in RELIGION:
        return RELIGION[value]

    remark = translate_remark(value.lstrip('NA,').strip())
    if remark:
        remarks.append(remark)

    return None


def build_speakers(rows, problems):
    """The whole speaker table, plus the identifiers it defines."""
    return [
        build_speaker(row, number, problems)
        for number, row in enumerate(rows, start=2)
    ]
