"""Writing the results of a search as one CSV file.

The rows come from the same serializer the result list uses, so the sentence
and the nearby word read exactly as they do on screen.
"""

import csv

from core.processing.exporting.csv_writer import cell
from core.serializers import TokenSearchResultSerializer

# More matches than this are refused: one file of them would be slow to build
# and too long to read. The reader is asked to narrow the search instead.
MAX_ROWS = 10_000

COLUMNS = [
    'text_name', 'sentence_id', 'speaker_name', 'source', 'lemma',
    'pos_tag', 'ud_type', 'context_source', 'sentence',
]

# Without this mark at the start Excel reads the file in the local 8-bit
# encoding and turns the Cyrillic into garbage.
BYTE_ORDER_MARK = '﻿'


def write_search_csv(file, queryset):
    """Write the matches of a search into ``file``: a header, then one row each.

    Example row: Печалбари,1,Антон Панов,убаво,убав,Rgp,advmod,,Комедијата е убаво напишана.
    """
    file.write(BYTE_ORDER_MARK)
    writer = csv.writer(file)
    writer.writerow(COLUMNS)

    for result in TokenSearchResultSerializer(queryset, many=True).data:
        writer.writerow([cell(result[name]) for name in COLUMNS])
