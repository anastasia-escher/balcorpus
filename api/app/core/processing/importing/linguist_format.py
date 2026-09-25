"""Reading an annotation file exactly as the linguists send it.

Their files differ from the corpus format in a few small ways, and this module
bridges each of them, so a file can be imported without converting it first:

* the column with the syntactic head is called ``ud_valency``, and the one
  with the speaker ``speaker``;
* ``text_id`` holds the Macedonian title of the text, "Печалбари", rather
  than its identifier "panov_pechalbari_1936";
* the speaker column holds a name, "Антон Панов", rather than "anton_panov";
* the first row of some files holds nothing but an invisible byte order mark.

A file already in the corpus format goes through unchanged: an identifier
that is known is simply kept.
"""

from collections import defaultdict

from core.models import Speaker, Text

from .cleaning import clean_label
from .columns import HEAD_COLUMN, SPEAKER_COLUMN

# What a column is called in the linguists' files -> what the importer calls it.
LINGUIST_COLUMN_NAMES = {
    'ud_valency': HEAD_COLUMN,
    'speaker': SPEAKER_COLUMN,
}


def use_corpus_column_names(row):
    """Rename the linguists' columns to the corpus names.

    Example: {'ud_valency': 3, 'speaker': 'Антон Панов', ...}
          -> {'head': 3, 'speaker_id': 'Антон Панов', ...}
    """
    renamed = {}
    for column, value in row.items():
        renamed[LINGUIST_COLUMN_NAMES.get(column, column)] = value

    return renamed


def drop_rows_without_a_word(rows, problems):
    """Leave out rows with neither a word form nor a lemma.

    Such a row is not a token. In the linguists' files it is the byte order
    mark at the very start, which Excel shows as an invisible word. Each one
    is mentioned, so a real token that lost its word does not vanish unseen.
    """
    kept = []
    for row in rows:
        fields = row['fields']
        if fields['source'] is None and fields['lemma'] is None:
            problems.warning('no word form and no lemma, so the row was left out', row['row_number'])
            continue
        kept.append(row)

    return kept


def find_text_ids(rows, chosen_text_id, problems):
    """Replace the title in each row's text_id with the text's identifier.

    ``chosen_text_id`` comes from ``--text`` on the command line and wins over
    whatever the file says. Otherwise a known identifier is kept, and a title
    is looked up among the texts. A title that belongs to two texts is not
    guessed at: the error names both, so the right one can be passed with
    ``--text``. An unknown title is left as it is, and the later check that
    every text exists reports it.
    """
    if chosen_text_id:
        for row in rows:
            row['text_id'] = chosen_text_id
        return

    known_ids = set(Text.objects.values_list('text_id', flat=True))

    ids_by_title = defaultdict(list)
    for text_id, title in Text.objects.values_list('text_id', 'text_name'):
        ids_by_title[title].append(text_id)

    reported = set()
    for row in rows:
        written = row['text_id']
        if written is None or written in known_ids:
            continue

        matching_ids = ids_by_title.get(clean_label(written), [])
        if len(matching_ids) == 1:
            row['text_id'] = matching_ids[0]
        elif len(matching_ids) > 1 and written not in reported:
            reported.add(written)
            problems.error(
                f"several texts are called '{written}': {', '.join(sorted(matching_ids))}. "
                'Run the command again with --text and the right one'
            )


def find_speaker_ids(rows, problems):
    """Replace a speaker's name in each row with the speaker's identifier.

    A known identifier is kept. A name that two speakers share is reported
    rather than guessed at; an unknown name is left as it is, and the check of
    the speakers reports it.
    """
    known_ids = set(Speaker.objects.values_list('speaker_id', flat=True))

    ids_by_name = defaultdict(list)
    for speaker_id, name in Speaker.objects.values_list('speaker_id', 'full_name'):
        ids_by_name[name].append(speaker_id)

    reported = set()
    for row in rows:
        written = row['speaker_slug']
        if written is None or written in known_ids:
            continue

        matching_ids = ids_by_name.get(clean_label(written), [])
        if len(matching_ids) == 1:
            row['speaker_slug'] = matching_ids[0]
        elif len(matching_ids) > 1 and written not in reported:
            reported.add(written)
            problems.error(
                f"several speakers are called '{written}': {', '.join(sorted(matching_ids))}. "
                'Write the right speaker_id into the file instead of the name',
                row['row_number'],
            )
