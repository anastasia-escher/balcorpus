"""Turning raw spreadsheet cells into values worth storing.

There are three levels of cleaning here, and the difference matters:

* ``clean_text`` only trims whitespace.  It is what the word forms and lemmas
  of the corpus go through, because changing a single letter of the source
  material would be falsifying the data.
* ``clean_annotation`` additionally reads "_" as "no value", which is the
  Universal Dependencies convention for an empty annotation field.
* ``clean_label`` additionally reads "NA" as "no value" and repairs Latin
  letters that were typed inside Cyrillic words.  It is for metadata only.
"""

import re

# How the metadata tables write "there is nothing here".  Note that "-" is
# deliberately not in this set: a hyphen is a real token in the corpus.
MISSING_LABELS = {'NA', 'N/A', 'n/a'}

# Universal Dependencies writes an empty annotation field as a single "_".
UD_EMPTY_FIELD = '_'

# The metadata tables mix Latin letters into Cyrillic words, because the two
# alphabets share letter shapes: "Jугозапад" is typed with a Latin J and
# "Диjалектен" with a Latin j.  They look identical but compare as different
# strings, so filtering by variety would silently miss half the rows.
LATIN_TO_CYRILLIC = str.maketrans({
    'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'Н', 'J': 'Ј', 'K': 'К',
    'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х',
    'a': 'а', 'c': 'с', 'e': 'е', 'j': 'ј', 'o': 'о', 'p': 'р', 'x': 'х',
    'y': 'у',
})

FIRST_CYRILLIC_CHARACTER = 'Ѐ'
LAST_CYRILLIC_CHARACTER = 'ӿ'

# How a yes/no cell may be written. The editors work in several languages,
# so each answer is accepted in the ones they use. Compared in lower case.
YES_VALUES = {'yes', 'y', 'true', '1', 'ja', 'да', 'д'}
NO_VALUES = {'no', 'n', 'false', '0', 'nein', 'нет', 'не', 'н'}

# Gender is written sometimes with a Latin M, sometimes with a Cyrillic М.
# It is a closed set of values, so it gets an explicit mapping.
GENDER_VALUES = {'M': 'М', 'М': 'М', 'F': 'Ж', 'Ж': 'Ж', 'W': 'Ж'}

# A word is a run of letters and digits.  The underscore is left out on
# purpose, although \w would match it: "Пустина_processed_FINAL" is three
# words, and only the Cyrillic one may have its letters changed.
WORD_PATTERN = re.compile(r'[^\W_]+')


def has_cyrillic(text):
    """True if the string contains at least one Cyrillic letter."""
    return any(
        FIRST_CYRILLIC_CHARACTER <= character <= LAST_CYRILLIC_CHARACTER
        for character in text
    )


def fix_word(word):
    """Repair one word, if it mixes the two alphabets."""
    if not has_cyrillic(word):
        return word

    return word.translate(LATIN_TO_CYRILLIC)


def fix_alphabet(text):
    """Replace Latin look-alike letters inside otherwise Cyrillic words.

    The repair is done word by word rather than over the whole string, because
    a purely Latin word standing next to Cyrillic ones is meant to be Latin:
    in "NA (амб – Полска)" the "NA" has to survive untouched.

    Examples:
        "Диjалектен" (Latin j)  -> "Дијалектен" (Cyrillic ј)
        "NA (амб – Боливиjа)"   -> "NA (амб – Боливија)"
        "vasil_iljoski"         -> unchanged
        "Пустина_processed"     -> unchanged
    """
    return WORD_PATTERN.sub(lambda match: fix_word(match.group()), text)


def clean_text(value):
    """Trim a cell into a string, or None when the cell is empty.

    Nothing inside the text is changed, so this is safe for corpus material.

    Example: "  молим " -> "молим", "" -> None, 1937 -> "1937"
    """
    if value is None:
        return None

    text = str(value).replace('﻿', '').strip()
    return text or None


def clean_annotation(value):
    """Like clean_text, but the UD placeholder "_" also counts as empty.

    Example: "Case=Nom|Gender=Masc" stays, "_" -> None
    """
    text = clean_text(value)
    if text == UD_EMPTY_FIELD:
        return None

    return text


def clean_label(value):
    """Clean a metadata value: "NA" means empty, and the alphabet is repaired.

    Example: "NA" -> None, "Jугозапад" -> "Југозапад"
    """
    text = clean_text(value)
    if text is None or text in MISSING_LABELS:
        return None

    return fix_alphabet(text)


def clean_number(value):
    """Read a cell as an integer, or None when it does not hold one.

    Example: "1902" -> 1902, "" -> None, "um 1900" -> None
    """
    text = clean_text(value)
    if text is None:
        return None

    try:
        return int(float(text))
    except ValueError:
        return None


def clean_yes_no(value):
    """Read a yes/no cell as True or False, or None when it is empty or unclear.

    Example: "yes" -> True, "Нет" -> False, 0 -> False, "" -> None, "maybe" -> None
    """
    text = clean_text(value)
    if text is None:
        return None

    answer = text.lower()
    if answer in YES_VALUES:
        return True
    if answer in NO_VALUES:
        return False

    return None


def clean_gender(value):
    """Normalise a gender cell to a single Cyrillic letter, М or Ж."""
    text = clean_label(value)
    if text is None:
        return None

    return GENDER_VALUES.get(text, text)
