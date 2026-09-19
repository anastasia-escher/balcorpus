"""Turning the document spreadsheet into the corpus text table.

What changes on the way:

* ``Text_ID`` held a running number and ``text_id`` held a file name, so
  neither could be used to refer to a text; both are replaced by one readable
  identifier, ``panov_pechalbari_1936``, and the file name is kept as the
  record of where the text came from;
* the author is worked out from that file name and recorded as ``author_id``,
  which is the cross-reference the annotation files and the speaker table
  share;
* genre and variety become the English vocabularies, with whatever the source
  wrote beside them kept in ``variety_note``;
* a date cell naming two years keeps both.
"""

import re

from .authors import find_author
from .fields import Unknown, clean, read_text_variety, read_years, translate_list
from .slugs import text_slug
from .vocabularies import DATA_GENRE, TEXT_GENRE

# One title cell holds the title, a long run of spaces, and then the list of
# writers an anthology collects. The run of spaces is what separates the two.
TITLE_AND_CONTRIBUTORS = re.compile(r'\s{3,}')

CONTRIBUTORS_PREFIX = 'Contributors: '

COLUMNS = [
    'text_id',
    'title',
    'author_id',
    'data_genre',
    'text_genre',
    'variety',
    'variety_note',
    'year',
    'year_note',
    'source_url',
    'source_file',
    'source_row',
    'short_description',
]


def collect(value, problems, row_number):
    """Keep a translated value, or record it as untranslated and drop it."""
    if isinstance(value, Unknown):
        problems.append(f'texts row {row_number}: no translation for {value}')
        return None

    return value


def join(values):
    """Several values in one cell, as the data dictionary describes them."""
    return ';'.join(value for value in values if value)


def split_title(title):
    """Separate a title from the list of writers an anthology collects.

    One cell reads "Раскази за деца" followed by a long run of spaces and then
    twenty names in brackets. The names belong to the text but they are not
    its title.

    Example: split_title('Раскази за деца     (Ванчо Николески, ...)')
             -> ('Раскази за деца', 'Contributors: Ванчо Николески, ...')
    """
    parts = TITLE_AND_CONTRIBUTORS.split(title, maxsplit=1)
    if len(parts) == 1:
        return title.strip(), ''

    head, tail = parts
    contributors = tail.strip().strip('()').strip()
    if not contributors:
        return head.strip(), ''

    return head.strip(), CONTRIBUTORS_PREFIX + contributors


def build_text(row, row_number, speakers_by_name, speaker_ids, problems):
    """One row of the source as one row of the text table."""
    title, contributors = split_title(clean(row.get('Titel')) or '')
    file_name = clean(row.get('text_id')) or ''

    author = find_author(file_name, speakers_by_name)
    if author is None:
        problems.append(
            f'texts row {row_number}: no speaker matches the file name '
            f'{file_name!r}, so "{title}" has no author'
        )

    years = read_years(row.get('Date'))
    varieties, variety_note = read_text_variety(clean(row.get('Variety')))
    genres = translate_list(clean(row.get('Text_Genre')), TEXT_GENRE, 'Text_Genre')

    # The identifier reads better with the author in front; a text whose
    # author is unknown is named after its title alone.
    author_name = author['speaker'] if author else ''

    return {
        'text_id': text_slug(author_name, title, years[0] if years else None),
        'title': title,
        'author_id': speaker_ids[author['speaker']] if author else '',
        'data_genre': collect(
            translate_list(clean(row.get('Data_Genre')), DATA_GENRE, 'Data_Genre')[0]
            if clean(row.get('Data_Genre')) else None,
            problems, row_number,
        ) or '',
        'text_genre': join(collect(genre, problems, row_number) for genre in genres),
        'variety': join(collect(variety, problems, row_number) for variety in varieties),
        'variety_note': variety_note or '',
        'year': years[0] if years else '',
        # A text published twice keeps both years; the first one is the year.
        'year_note': ', '.join(str(year) for year in years[1:]),
        'source_url': clean(row.get('Source')) or '',
        'source_file': file_name,
        'source_row': row.get('Text_ID') or '',
        'short_description': contributors,
    }


def build_texts(rows, speakers_by_name, speaker_ids, problems):
    """The whole text table."""
    return [
        build_text(row, number, speakers_by_name, speaker_ids, problems)
        for number, row in enumerate(rows, start=2)
    ]
