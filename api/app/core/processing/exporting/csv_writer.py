"""Writing one table of the corpus as a CSV file.

The files are read on the server by PHP, whose ``fgetcsv()`` understands the
same dialect Python's ``csv`` module writes: comma separated, quotation marks
around any cell that contains a comma, a quotation mark or a line break.  The
descriptions of the texts contain all three, so the quoting is not optional.
"""

import csv
import os
from pathlib import Path

# What a NULL looks like in a CSV cell.  The loader on the server turns an
# empty cell back into NULL; no field of the corpus is one where an empty
# string would mean something different from "nothing".
EMPTY_CELL = ''


def cell(value):
    """One database value as it is written into a CSV cell.

    Example: cell(None) -> '', cell(1936) -> '1936', cell('Печалбари') -> 'Печалбари',
             cell(True) -> '1', cell(False) -> '0'
    """
    if value is None:
        return EMPTY_CELL

    # MariaDB stores a yes/no column as the number 1 or 0, so that is what
    # the loader should find, not Python's "True" and "False".
    if value is True:
        return '1'
    if value is False:
        return '0'

    return str(value)


def write_csv(path, column_names, rows):
    """Write one CSV file: a header line, then one line per row.

    ``rows`` is any iterable of dicts keyed by column name, so a queryset can
    be streamed into the file rather than held in memory all at once:

        [{'text_id': 'panov_pechalbari_1936', 'text_name': 'Печалбари'}, ...]

    A column a row does not carry is written as an empty cell, so the file
    always has the same shape as its header.

    Returns how many rows were written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    written = 0

    # The rows go into a temporary file first, which replaces the real one
    # only once it is complete.  A run that stops halfway then leaves the old
    # file in place, not a cut-off one that would wipe data on the server.
    temporary_path = path.with_name(path.name + '.tmp')

    # newline='' lets the csv module decide the line endings itself; without it
    # every row gains a blank line on some platforms.
    with open(temporary_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)

        for row in rows:
            writer.writerow([cell(row.get(name)) for name in column_names])
            written += 1

    os.replace(temporary_path, path)
    return written
