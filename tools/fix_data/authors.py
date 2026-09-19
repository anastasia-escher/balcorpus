"""Working out which speaker wrote which text.

The metadata table of the documents has no author column: the only trace of
the author is inside the original file name, and that name is written in half
a dozen different shapes — "06 в) vasil iljoski - corbadji teodos", "9 Стале
Попов - Калеш Анѓа", "Чачански Крсте На небото книга", "Ѓурчинов По трагите".
Rather than trying to parse those, every speaker is looked for inside the file
name.

Matching on the surname alone was tried and thrown away: "Миле Неделковски"
would then have been filed under the only Неделковски in the speaker table,
Велко, who is a different writer. In a scholarly corpus a wrong attribution is
worse than a missing one, so everything the plain rule cannot resolve is
listed below by hand instead.
"""

from .slugs import slugify

# File names that spell an author differently from the speaker table, or give
# only part of the name. Each entry says: this file name really means this
# speaker. Kept explicit rather than solved by guessing, so that every
# attribution stays reviewable.
NAME_CORRECTIONS = {
    'ivan_dzheparovski': 'Иван Џепароски',       # table: Џепароски, file: Џепаровски
    'petre_m_andreevski': 'Петре Мито Андреевски',  # file abbreviates the middle name
    'jocikj_svetlana': 'Светлана Христова-Јоциќ',   # file drops the first surname
    'gjurchinov': 'Милан Ѓурчинов',              # file gives the surname only
    'stardelov': 'Георги Старделов',             # file gives the surname only
    'zaev': 'Зоран Заев',                        # file gives a romanised surname
}


def name_words(name):
    """The words of a name, as identifier words.

    Example: name_words('Стале Попов') -> {'stale', 'popov'}
    """
    return {word for word in slugify(name).split('_') if word}


def find_author(file_name, speakers_by_name):
    """Find the speaker whose name appears in the file name.

    A correction from the table above wins. Otherwise a speaker matches when
    every word of their name occurs in the file name, in any order, so both
    "Стале Попов - Калеш Анѓа" and "Чачански Крсте На небото книга" are
    recognised. When several speakers fit, the one with the most words wins,
    as the more specific match.

    Returns the speaker record, or None when nobody matches.
    """
    words_in_file = name_words(file_name)

    for pattern, speaker_name in NAME_CORRECTIONS.items():
        if name_words(pattern) <= words_in_file:
            return speakers_by_name.get(speaker_name)

    full_matches = [
        (len(name_words(name)), speaker)
        for name, speaker in speakers_by_name.items()
        if name_words(name) and name_words(name) <= words_in_file
    ]
    if not full_matches:
        return None

    full_matches.sort(key=lambda match: match[0], reverse=True)
    return full_matches[0][1]
