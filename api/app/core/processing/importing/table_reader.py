"""Reading a spreadsheet as a sequence of rows keyed by column name.

Both the metadata tables (.csv) and the annotation files (.xlsx) are read
here, so the importers never have to care which of the two they were given,
and never have to count columns by position.
"""

import csv
from pathlib import Path

import openpyxl

CSV_SUFFIX = '.csv'
EXCEL_SUFFIX = '.xlsx'
SUPPORTED_SUFFIXES = (CSV_SUFFIX, EXCEL_SUFFIX)


def clean_header(name):
    """Tidy one column heading.

    Leading byte order marks and trailing spaces are removed, because both
    occur in the real files: the annotation sheet has a column called
    "speaker " with a space at the end.

    The capitalisation is deliberately left alone: the metadata table has a
    column "Text_ID" and a *different* column "text_id", and lowercasing the
    headings would merge the two.
    """
    if name is None:
        return None

    return str(name).replace('﻿', '').strip()


def is_empty_row(values):
    """True for the blank rows the annotation files put between sentences."""
    return all(value is None or str(value).strip() == '' for value in values)


def check_for_duplicates(headers, path):
    """Refuse a file whose columns cannot be told apart.

    Earlier versions of the annotation sheet had two columns both named
    "POS_Tag"; reading such a file by name would silently drop one of them.
    """
    seen = set()
    duplicates = set()
    for header in headers:
        if header in seen:
            duplicates.add(header)
        seen.add(header)

    if duplicates:
        raise ValueError(
            f"{path} has more than one column named {', '.join(sorted(duplicates))}. "
            "Please give each column its own name and export the file again."
        )


def check_row_width(values, headers, path, row_number):
    """Refuse a row that has more values than the file has columns.

    zip() would silently throw the extra values away, and every value after the
    mistake would land in the wrong field.  That happens with an unquoted comma
    inside a cell, which is easy to produce and impossible to notice later.

    The count has to be exact rather than forgiving: a row that both gained a
    value from a stray comma and ended with an empty one adds up to the right
    width again, and the shift would go unnoticed.

    A row with *fewer* values is fine; it just means the last columns were left
    empty, which spreadsheets do all the time.
    """
    if len(values) > len(headers):
        raise ValueError(
            f"Row {row_number} of {path} has {len(values)} values but the file has "
            f"{len(headers)} columns. A cell most likely contains a comma without "
            "being wrapped in quotation marks, which splits it into two columns."
        )


def read_rows(path):
    """Yield every non-empty data row of the file as a dict.

    Example for one row of an annotation file:
    {'sent_id': 2, 'ud_id': 1, 'source': 'Васил', 'lemma': 'васил', ...}
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == EXCEL_SUFFIX:
        return read_excel_rows(path)
    if suffix == CSV_SUFFIX:
        return read_csv_rows(path)

    raise ValueError(
        f"{path} has the unsupported extension '{suffix}'. "
        f"Expected one of: {', '.join(SUPPORTED_SUFFIXES)}."
    )


def read_excel_rows(path):
    """Read the first worksheet of an .xlsx file, one row at a time.

    read_only mode means even a file with hundreds of thousands of rows is
    streamed rather than held in memory all at once.
    """
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook[workbook.sheetnames[0]]

    rows = worksheet.iter_rows(values_only=True)
    headers = [clean_header(name) for name in next(rows, [])]
    check_for_duplicates(headers, path)

    for row_number, values in enumerate(rows, start=2):
        if is_empty_row(values):
            continue
        check_row_width(values, headers, path, row_number)
        yield dict(zip(headers, values))

    workbook.close()


def read_csv_rows(path):
    """Read a .csv file, one row at a time."""
    with open(path, newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file)
        headers = [clean_header(name) for name in next(reader, [])]
        check_for_duplicates(headers, path)

        for row_number, values in enumerate(reader, start=2):
            if is_empty_row(values):
                continue
            check_row_width(values, headers, path, row_number)
            yield dict(zip(headers, values))
