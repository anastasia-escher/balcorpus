"""Converting the editors' spreadsheets into the corpus data set.

Run from the repository root:

    python -m tools.fix_data.run

It reads the workbooks the editors sent, writes the cleaned tables as Excel
workbooks in data/fixed_data, and prints everything it could not translate or
could not match, so the gaps are visible rather than silent.
"""

import sys
from pathlib import Path

import openpyxl

from .build_annotations import COLUMNS as ANNOTATION_COLUMNS
from .build_annotations import build_annotations
from .build_speakers import COLUMNS as SPEAKER_COLUMNS
from .build_speakers import build_speakers
from .build_texts import COLUMNS as TEXT_COLUMNS
from .build_texts import build_texts
from .schema import ANNOTATIONS, SPEAKERS, TEXTS, numeric_columns
from .write_docs import write_docs
from .write_tables import write_table

SOURCE_DIRECTORY = Path('/Users/aesche/PycharmProjects/BalcanCorpus/data/data_to_be_fixed')
OUTPUT_DIRECTORY = Path('data/fixed_data')

DOCUMENTS_FILE = '2026_06_01_Macedonian_Corpus_Metadata_Documents_Excel.xlsx'
SPEAKERS_FILE = '2026_06_01_Macedonian_Corpus_Metadata_Speakers_New.xlsx'
ANNOTATION_FILES = ['06 б) anton panov - pecalbari_processed_FINAL.xlsx']

# Authors of one of the texts who are missing from the speaker table. They are
# added with their name only, so the text still has an author and the gap is
# stated rather than hidden or invented. Listed by hand, like every other
# correction, so that each one stays reviewable.
AUTHORS_MISSING_FROM_SPEAKER_TABLE = [
    'Миле Неделковски',
    'Катица Ќулафкова',
    'Славе Ѓ. Димовски',
]

MISSING_METADATA_NOTE = 'metadata not supplied by the editors'


def rows_for_missing_authors():
    """Source-shaped rows for the authors the speaker table left out."""
    return [
        {'speaker': name, 'Full_Name': name}
        for name in AUTHORS_MISSING_FROM_SPEAKER_TABLE
    ]


def read_workbook(path):
    """Every non-empty row of the first worksheet, as dicts keyed by column."""
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook[workbook.sheetnames[0]]

    rows = worksheet.iter_rows(values_only=True)
    headers = [str(name).strip() if name else name for name in next(rows)]

    records = [
        dict(zip(headers, values))
        for values in rows
        if not all(value is None or str(value).strip() == '' for value in values)
    ]
    workbook.close()
    return records


def convert():
    """Read the source workbooks and write the cleaned data set."""
    problems = []

    speaker_rows = read_workbook(SOURCE_DIRECTORY / SPEAKERS_FILE)
    speaker_rows += rows_for_missing_authors()
    document_rows = read_workbook(SOURCE_DIRECTORY / DOCUMENTS_FILE)

    speakers = build_speakers(speaker_rows, problems)
    for speaker in speakers[-len(AUTHORS_MISSING_FROM_SPEAKER_TABLE):]:
        speaker['notes'] = MISSING_METADATA_NOTE
    speakers_by_name = {row['speaker']: row for row in speaker_rows}
    speaker_ids = {
        row['speaker']: built['speaker_id']
        for row, built in zip(speaker_rows, speakers)
    }

    texts = build_texts(document_rows, speakers_by_name, speaker_ids, problems)

    write_table(OUTPUT_DIRECTORY, 'speakers', SPEAKER_COLUMNS, speakers,
                numeric_columns(SPEAKERS))
    write_table(OUTPUT_DIRECTORY, 'texts', TEXT_COLUMNS, texts,
                numeric_columns(TEXTS))
    print(f'speakers.xlsx: {len(speakers)} rows')
    print(f'texts.xlsx:    {len(texts)} rows')

    texts_by_source_file = {text['source_file']: text for text in texts}
    for file_name in ANNOTATION_FILES:
        convert_annotations(file_name, texts_by_source_file, problems)

    write_docs(OUTPUT_DIRECTORY)
    print('README.md and datapackage.json written')

    report(problems)
    return problems


def convert_annotations(file_name, texts_by_source_file, problems):
    """Convert one annotated text, naming it after the text it belongs to."""
    source_file = Path(file_name).stem
    text = texts_by_source_file.get(source_file)
    if text is None:
        problems.append(
            f'{file_name}: no row of texts.csv has this as its source_file, '
            'so the annotation cannot be linked to a text'
        )
        return

    rows = read_workbook(SOURCE_DIRECTORY / file_name)
    tokens = build_annotations(rows, text['text_id'], text['author_id'], problems)

    write_table(OUTPUT_DIRECTORY / 'annotations', text['text_id'],
                ANNOTATION_COLUMNS, tokens, numeric_columns(ANNOTATIONS))
    print(f"{text['text_id']}.xlsx: {len(tokens)} tokens")


def report(problems):
    """Print what the conversion could not do, so nobody has to go looking."""
    if not problems:
        print('\nNothing was left untranslated or unmatched.')
        return

    print(f'\n{len(problems)} things need a human decision:')
    for problem in problems:
        print(f'  {problem}')


if __name__ == '__main__':
    sys.exit(0 if not convert() else 0)
