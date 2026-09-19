"""Building the identifiers that tie the corpus files together.

An identifier is lowercase ASCII with underscores, so it survives every
spreadsheet, every export and every URL unchanged. Speakers are named after
the person, texts after their author, a short title and the year.
"""

import re

from .transliterate import to_latin

NON_IDENTIFIER_CHARACTERS = re.compile(r'[^a-z0-9]+')

# File names sometimes glue the running number to the first word, as in
# "61Тодор Чаловски". A digit next to a letter starts a new word.
DIGIT_LETTER_BOUNDARY = re.compile(r'(?<=\d)(?=[a-z])|(?<=[a-z])(?=\d)')

# Words that add nothing to a text identifier but a lot to its length.
TITLE_STOPWORDS = {'na', 'i', 'se', 'the', 'a', 'od', 'vo', 'za', 'so'}

# How many words of the title go into the identifier.
TITLE_WORD_LIMIT = 3


def slugify(text):
    """Reduce any text to lowercase ASCII words joined by underscores.

    Example: slugify('Ѓорѓи Абаџиев') -> 'gjorgji_abadzhiev'
    """
    latin = to_latin(text or '').lower()
    separated = DIGIT_LETTER_BOUNDARY.sub('_', latin)
    return NON_IDENTIFIER_CHARACTERS.sub('_', separated).strip('_')


def speaker_slug(name):
    """The identifier of one person.

    Example: speaker_slug('Антон Панов') -> 'anton_panov'
    """
    return slugify(name)


def title_words(title):
    """The words of a title that are worth putting into an identifier."""
    words = [word for word in slugify(title).split('_') if word]
    kept = [word for word in words if word not in TITLE_STOPWORDS]
    return (kept or words)[:TITLE_WORD_LIMIT]


def text_slug(author_name, title, year):
    """The identifier of one text: author surname, short title, year.

    Example: text_slug('Антон Панов', 'Печалбари', 1936) -> 'panov_pecalbari_1936'
    """
    author_words = [word for word in slugify(author_name).split('_') if word]
    surname = author_words[-1] if author_words else 'unknown'

    parts = [surname] + title_words(title)
    if year:
        parts.append(str(year))

    return '_'.join(parts)
