"""Writing the data dictionary that ships beside the data.

Two files come out of the schema: ``datapackage.json`` for tools and
``README.md`` for people.
"""

import json
from datetime import date

from .schema import LANGUAGE_CODES, RESOURCES

PACKAGE_NAME = 'macedonian-corpus'
PACKAGE_TITLE = 'Macedonian Corpus — metadata and annotated texts'
PACKAGE_DESCRIPTION = (
    'Metadata and morphologically and syntactically annotated texts of the '
    'Macedonian Corpus. The metadata are in English; the material itself, and '
    'the names of people and titles, stay in Macedonian.'
)


def datapackage():
    """The machine-readable description of the data set."""
    return {
        'name': PACKAGE_NAME,
        'title': PACKAGE_TITLE,
        'description': PACKAGE_DESCRIPTION,
        'created': date.today().isoformat(),
        'profile': 'tabular-data-package',
        'resources': [
            {
                'name': resource['name'],
                'path': resource['path'],
                'title': resource['title'],
                'description': resource['description'],
                'profile': 'tabular-data-resource',
                'format': 'xlsx',
                'mediatype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'dialect': {'header': True, 'headerRows': [1]},
                'schema': {
                    'fields': resource['fields'],
                    'primaryKey': resource['primaryKey'],
                    'foreignKeys': resource.get('foreignKeys', []),
                    'missingValues': [''],
                },
            }
            for resource in RESOURCES
        ],
    }


def field_lines(resource):
    """One Markdown table row per column of a resource."""
    lines = ['| column | type | meaning |', '|---|---|---|']
    for entry in resource['fields']:
        meaning = entry['description']
        if 'enum' in entry:
            meaning += ' One of: ' + ', '.join(f'`{value}`' for value in entry['enum']) + '.'
        if 'example' in entry:
            meaning += f" Example: `{entry['example']}`."
        lines.append(f"| `{entry['name']}` | {entry['type']} | {meaning} |")

    return lines


def readme():
    """The data dictionary, as Markdown."""
    lines = [
        f'# {PACKAGE_TITLE}',
        '',
        PACKAGE_DESCRIPTION,
        '',
        'These files are produced from the spreadsheets the editors maintain, by',
        '`python -m tools.fix_data.run` in the repository root. Edit the',
        'spreadsheets and run it again rather than editing these files by hand.',
        '',
        '## How the files fit together',
        '',
        '```',
        'speakers.xlsx          one row per person        speaker_id',
        '        ▲                                              ▲',
        '        │ author_id                                    │ speaker_id',
        'texts.xlsx              one row per document      text_id',
        '        ▲                                              ▲',
        '        │ text_id                                      │',
        'annotations/<text_id>.xlsx    one row per token',
        '```',
        '',
        'Every identifier is lowercase ASCII with underscores, so it survives',
        'spreadsheets, exports and URLs unchanged.',
        '',
        '## Conventions',
        '',
        '- **The format is Excel (`.xlsx`)**, one table per workbook, the column',
        '  names in row 1 and the data from row 2. Excel carries its own encoding,',
        '  so nothing has to be set when opening a file and no accented or',
        '  Cyrillic letter can turn into `Ð¿Ð°Ð½Ð¾Ð²`. A comma inside a cell is',
        '  just a comma, because there is no delimiter to escape.',
        '- **Numbers are stored as numbers** — years, sentence and token numbers,',
        '  the head position — and everything else as text.',
        '- **An empty cell means the value was not recorded.** The sources wrote',
        '  `NA` for this, which is a value and not an absence, so it is gone.',
        '- **A cell that holds several values** separates them with a semicolon,',
        '  as in `drama;prose` or `sr;hr`.',
        '- **Languages** are ISO 639-1 codes: '
        + ', '.join(f'`{code}`' for code in LANGUAGE_CODES) + '.',
        '- **Macedonian is romanised** by the standard transliteration with the',
        '  diacritics spelled out: `ж` → `zh`, `ч` → `ch`, `џ` → `dzh`, `ѓ` → `gj`,',
        '  `ќ` → `kj`, `љ` → `lj`, `њ` → `nj`, `ѕ` → `dz`.',
        '',
    ]

    for resource in RESOURCES:
        lines += [
            f"## {resource['path']}",
            '',
            resource['description'],
            '',
        ]
        lines += field_lines(resource)
        lines.append('')

    lines += [
        '## Known gaps',
        '',
        'The conversion prints everything it cannot translate or match. What it',
        'reported last time is recorded here:',
        '',
        '- Three authors write a text but are missing from the speaker',
        '  spreadsheet: Миле Неделковски, Катица Ќулафкова and Славе Ѓ. Димовски.',
        '  They appear in `speakers.xlsx` with their name only, and their `notes`',
        '  say so.',
        '- The first row of the annotation file held a byte order mark and no',
        '  word, so it is not a token and was dropped.',
        '',
    ]

    return '\n'.join(lines)


def write_docs(directory):
    """Write both files into the data directory."""
    (directory / 'datapackage.json').write_text(
        json.dumps(datapackage(), ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    (directory / 'README.md').write_text(readme(), encoding='utf-8')
