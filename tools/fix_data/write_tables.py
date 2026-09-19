"""Writing one table of the corpus to disk as an Excel workbook.

Excel is the format everyone works in: the editors open it directly, and the
importer reads it. It also settles the two things that went wrong with CSV —
the encoding is inside the file, so no reader has to guess it and nobody sees
`Ð¿Ð°Ð½Ð¾Ð²` instead of `панов`, and a comma inside a cell is just a comma,
with no delimiter to escape.
"""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

# How wide a column may get before it stops growing with its content.
MINIMUM_COLUMN_WIDTH = 10
MAXIMUM_COLUMN_WIDTH = 40

HEADER_ROW = 1

# Excel refuses a sheet name longer than this.
MAXIMUM_SHEET_NAME = 31


def looks_like_a_whole_number(value):
    """True for a string that is nothing but digits, e.g. '1936'."""
    return isinstance(value, str) and value.isdigit()


def cell_value(value, column, numeric_columns):
    """What to put in the cell: a number where a number belongs, else text.

    Only the columns the schema calls numeric are converted, so a word form
    that happens to read '5' stays the text it is.
    """
    if value in (None, ''):
        return None

    if column in numeric_columns and looks_like_a_whole_number(value):
        return int(value)

    return value


def column_widths(columns, records):
    """A width per column, from the longest value in it, within reason."""
    widths = []
    for column in columns:
        longest = max(
            [len(column)] + [len(str(record.get(column) or '')) for record in records]
        )
        widths.append(min(max(longest + 2, MINIMUM_COLUMN_WIDTH), MAXIMUM_COLUMN_WIDTH))

    return widths


def write_table(directory, name, columns, records, numeric_columns=()):
    """Write one table as a worksheet the editors can work in directly.

    The header is bold, frozen and filterable, so a table of a hundred rows
    stays readable while scrolling.

    Returns the path written.
    """
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{name}.xlsx'

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = name[:MAXIMUM_SHEET_NAME]

    sheet.append(list(columns))
    for cell in sheet[HEADER_ROW]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical='top')

    for record in records:
        sheet.append([
            cell_value(record.get(column), column, numeric_columns)
            for column in columns
        ])

    for number, width in enumerate(column_widths(columns, records), start=1):
        sheet.column_dimensions[get_column_letter(number)].width = width

    sheet.freeze_panes = 'A2'
    sheet.auto_filter.ref = sheet.dimensions

    workbook.save(path)
    return path
