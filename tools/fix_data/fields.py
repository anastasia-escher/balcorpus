"""Reading one cell of the source spreadsheets into a clean value.

Every function here takes what the editors typed and returns either a value
that belongs to a controlled vocabulary, or None when the cell says nothing.
Anything that cannot be translated is handed back as an "unknown" so that the
conversion can report it instead of quietly dropping it.
"""

import re

from .transliterate import fold_lookalikes, to_latin
from .vocabularies import (
    DIALECT_REGION,
    EDUCATION_LEVEL,
    EDUCATION_NOTE,
    LANGUAGE,
    MISSING,
    NOTE_PHRASES,
    PLACES_IN_NOTES,
    TEXT_VARIETY,
)

# "NA (амб – Либан, Полска)": no value, followed by a remark in brackets.
VALUE_WITH_REMARK = re.compile(r'^(?P<value>[^(]*?)\s*\((?P<remark>.*)\)\s*$')

# The source separates several values in one cell with a comma or a slash.
VALUE_SEPARATORS = re.compile(r'\s*[,/;]\s*')

YEAR = re.compile(r'\d{4}')

# The source capitalises the variety differently in different rows, so it is
# looked up in lowercase.
VARIETY_BY_LOWERCASE = {key.lower(): value for key, value in TEXT_VARIETY.items()}


class Unknown:
    """A value that no vocabulary covers, kept so it can be reported.

    Example: Unknown('Education', 'Докторат')
    """

    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __str__(self):
        return f'{self.field}: {self.value!r}'


def clean(value):
    """Trim a cell, folding Latin look-alikes back into Cyrillic.

    Returns None when the cell is empty or says "NA".

    Example: clean('  Jугозапад ') -> 'Југозапад', clean('NA') -> None
    """
    if value is None:
        return None

    text = str(value).replace('﻿', '').replace('\xa0', ' ').strip()
    if text in MISSING:
        return None

    return fold_lookalikes(text)


def split_value_and_remark(text):
    """Separate "NA (амб – Сенегал)" into its value and its remark."""
    match = VALUE_WITH_REMARK.match(text)
    if not match:
        return text, None

    value = match.group('value').strip()
    return (value if value not in MISSING else None), match.group('remark').strip()


def translate(text, vocabulary, field):
    """Look one value up in a vocabulary, or report it as unknown."""
    if text is None:
        return None

    return vocabulary.get(text, Unknown(field, text))


def translate_list(text, vocabulary, field):
    """Translate a cell that may hold several values, keeping their order.

    Example: translate_list('Драма, Проза', TEXT_GENRE, 'Text_Genre')
             -> ['drama', 'prose']
    """
    if text is None:
        return []

    return [
        translate(part, vocabulary, field)
        for part in VALUE_SEPARATORS.split(text)
        if part
    ]


def read_languages(text, field):
    """Read a language cell into ISO 639-1 codes and a remark, if any.

    Example: read_languages('SR/HR', 'L2')  -> (['sr', 'hr'], None)
             read_languages('NA (амб – Сенегал)', 'L3')
             -> ([], 'ambassador to Senegal')
    """
    if text is None:
        return [], None

    value, remark = split_value_and_remark(text)
    # A few rows write the code itself in Cyrillic — "МК" rather than "MK" —
    # so the cell is romanised before it is looked up.
    romanised = to_latin(value).upper() if value else None
    codes = translate_list(romanised, LANGUAGE, field)
    return codes, translate_remark(remark)


def translate_remark(remark):
    """Put a remark from the source into English, as far as it is understood.

    Example: 'амб – Либан, Етиопија' -> 'ambassador to Lebanon, Ethiopia'
    """
    if not remark:
        return None

    text = remark.replace('–', '-')
    for macedonian, english in NOTE_PHRASES.items():
        text = text.replace(macedonian, english)
    for macedonian, english in PLACES_IN_NOTES.items():
        text = text.replace(macedonian, english)

    text = re.sub(r'\s*-\s*', ' ', text).strip()
    # Whatever is still Cyrillic was not in any table, so it is transliterated
    # rather than dropped.
    return to_latin(text)


def read_education(text):
    """Read an education cell into a level and the detail in brackets.

    Example: 'Средно (гимназија)' -> ('secondary', 'gymnasium')
    """
    if text is None:
        return None, None

    value, remark = split_value_and_remark(text)
    level = None
    if value:
        level = EDUCATION_LEVEL.get(value.capitalize(), Unknown('Education', value))

    note = None
    if remark:
        note = '; '.join(
            EDUCATION_NOTE.get(part, to_latin(part))
            for part in remark.split(',')
            if part.strip()
        )

    return level, note


def read_region(text):
    """Read a dialect-area cell, which may name a country and a part of it.

    Example: 'Грција, североисток' -> 'Greece (northeast)'
    """
    if text is None:
        return None

    parts = [part for part in VALUE_SEPARATORS.split(text) if part]
    translated = [translate(part, DIALECT_REGION, 'Variety') for part in parts]

    unknown = [part for part in translated if isinstance(part, Unknown)]
    if unknown:
        return unknown[0]

    if len(translated) == 1:
        return translated[0]

    return f'{translated[0]} ({", ".join(translated[1:])})'


def read_text_variety(text):
    """Read a text's variety into controlled values and the detail beside it.

    The source writes the controlled word first and then, after a dash or in
    brackets, as much detail as it likes:

        'Стандарден'                            -> (['standard'], None)
        'Стандарден; дијалектен (воденски)'     -> (['standard', 'dialectal'],
                                                    'Vodenski')
        'Дијалектен – крушевски говор (западно наречје)'
                                                -> (['dialectal'],
                                                    'krushevski govor (zapadno narechje)')
    """
    if text is None:
        return [], None

    head, remark = split_value_and_remark(text)
    head = head or ''

    detail = None
    if '–' in head or '—' in head:
        head, _, detail = re.split(r'(\s*[–—]\s*)', head, maxsplit=1)
        detail = detail.strip()

    varieties = [
        VARIETY_BY_LOWERCASE.get(part.lower(), Unknown('Variety', part))
        for part in VALUE_SEPARATORS.split(head)
        if part.strip()
    ]

    parts = [part for part in (detail, remark) if part]
    return varieties, to_latin(' '.join(parts)).strip() or None


def read_years(text):
    """Every four-digit year in a cell, in the order they appear.

    Example: '1957, 1994' -> [1957, 1994], 1936 -> [1936]
    """
    if text is None:
        return []

    return [int(year) for year in YEAR.findall(str(text))]
