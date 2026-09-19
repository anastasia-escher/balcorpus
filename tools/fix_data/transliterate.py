"""Writing Macedonian Cyrillic in the Latin alphabet.

Identifiers and English metadata have to be plain ASCII, so the corpus uses
one transliteration everywhere: the standard Macedonian romanisation, with
the diacritics dropped (č -> ch, š -> sh) so that nothing but a-z remains.
"""

import re
import unicodedata

# Some files write Ѓ and Ќ as Г and К followed by a combining accent, which
# looks identical but is a different sequence of characters. Composing the
# text first means the table below sees one letter rather than two.
# An underscore does not join two words into one: "Поле_processed_FINAL" is a
# Cyrillic word next to a Latin one, and only the first should be folded.
WORD_PATTERN = re.compile(r'[^\W_]+')

# The source files mix Latin look-alikes into Cyrillic words: "Jугозапад" is
# typed with a Latin J, "Скопjе" with a Latin j. They are folded into their
# Cyrillic twins first, so the transliteration sees one alphabet only.
LATIN_LOOKALIKES = str.maketrans({
    'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'Н', 'J': 'Ј', 'K': 'К',
    'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х',
    'a': 'а', 'c': 'с', 'e': 'е', 'j': 'ј', 'o': 'о', 'p': 'р', 'x': 'х',
    'y': 'у',
})

MACEDONIAN_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ѓ': 'gj', 'е': 'e',
    'ж': 'zh', 'з': 'z', 'ѕ': 'dz', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l',
    'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'ќ': 'kj', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
    'ч': 'ch', 'џ': 'dzh', 'ш': 'sh',
    # Letters that only turn up in names borrowed from neighbouring alphabets.
    'ы': 'y', 'э': 'e', 'ю': 'ju', 'я': 'ja', 'й': 'j', 'щ': 'sht',
    'ъ': 'a', 'ь': '', 'ё': 'jo',
}


def has_cyrillic(text):
    """True if the string contains at least one Cyrillic letter."""
    return any('\u0400' <= character <= '\u04FF' for character in text)


def fold_word(word):
    """Repair one word, if it mixes the two alphabets."""
    return word.translate(LATIN_LOOKALIKES) if has_cyrillic(word) else word


def fold_lookalikes(text):
    """Turn Latin letters typed inside Cyrillic words back into Cyrillic.

    Words written wholly in Latin are left alone, so an already romanised
    name such as "anton panov" does not lose its p to a Cyrillic р.
    """
    return WORD_PATTERN.sub(lambda match: fold_word(match.group()), text)


def to_latin(text):
    """Transliterate Macedonian Cyrillic into plain Latin letters.

    Example: to_latin('Ѓорѓи Абаџиев') -> 'Gjorgji Abadzhiev'
    """
    folded = fold_lookalikes(unicodedata.normalize('NFC', text or ''))

    letters = []
    for character in folded:
        lower = character.lower()
        replacement = MACEDONIAN_TO_LATIN.get(lower)
        if replacement is None:
            letters.append(character)
            continue
        # A capital Cyrillic letter keeps its capital, even when it becomes
        # two Latin letters: Џ -> Dzh rather than DZH.
        letters.append(replacement.capitalize() if character.isupper() else replacement)

    return ''.join(letters)
