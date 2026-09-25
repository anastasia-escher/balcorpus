"""Writing the results of a search as one Excel file.

Excel rather than CSV because a CSV opens right in Excel only when its
separator matches the reader's regional settings: a comma for English, a
semicolon for Russian or German. An .xlsx file opens the same everywhere.
"""

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from core.serializers import TokenSearchResultSerializer

# More matches than this are refused: one file of them would be slow to build
# and too long to read. The reader is asked to narrow the search instead.
MAX_ROWS = 10_000

COLUMNS = [
    'text_id', 'text_name', 'sentence_id', 'speaker_id', 'speaker_name',
    'source', 'lemma', 'pos_tag', 'ud_type', 'context_source', 'sentence',
]


class SearchExportSerializer(TokenSearchResultSerializer):
    """A search result without the positions of its words.

    Those positions only tell the result list on the site what to mark; a
    spreadsheet has no use for them.
    """

    class Meta(TokenSearchResultSerializer.Meta):
        fields = COLUMNS


def text_cell(sheet, value):
    """A cell Excel shows exactly as written.

    openpyxl turns a string that starts with '=' into a formula, and Excel
    would run it; a cell marked as text is never run and never read as a date.

    Control characters (a stray tab-like byte pasted in from Word, say) are
    dropped: an .xlsx file cannot hold them, and openpyxl would refuse to
    write the whole file because of one of them.
    """
    value = ILLEGAL_CHARACTERS_RE.sub('', value)
    cell = WriteOnlyCell(sheet, value)
    cell.data_type = 's'
    return cell


def write_search_xlsx(file, queryset):
    """Write the matches of a search into ``file``: a header, then one row each.

    Example row: panov_pechalbari_1936 | Печалбари | 1 | anton_panov | Антон Панов |
    убаво | убав | Rgp | advmod | (empty) | Комедијата е убаво напишана.
    """
    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet('Search results')
    # The header stays in view while the reader scrolls.
    sheet.freeze_panes = 'A2'

    sheet.append(COLUMNS)

    for result in SearchExportSerializer(queryset, many=True).data:
        row = []
        for name in COLUMNS:
            value = result[name]
            if isinstance(value, str):
                row.append(text_cell(sheet, value))
            else:
                # The sentence number, kept a number so the column sorts
                # numerically, or an empty cell.
                row.append(value)
        sheet.append(row)

    workbook.save(file)
