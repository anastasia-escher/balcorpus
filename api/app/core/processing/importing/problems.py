"""Collecting everything wrong with a file, instead of stopping at the first.

An annotation file is written by hand, so it rarely contains exactly one
mistake.  Reporting them one at a time would mean the linguist fixes a row,
runs the import again, and finds the next one — twenty times over.  So the
whole file is checked first, nothing is written unless it is clean, and the
full list comes back at once.
"""

# A file whose columns have shifted produces a problem on every single row.
# Printing twenty-five thousand of them helps nobody.
MAX_REPORTED_PROBLEMS = 50


class ProblemList:
    """The problems found in one file, in the order they were found.

    Errors stop the import; warnings are worth seeing but let it through.
    """

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, message, row_number=None):
        self.errors.append(describe(message, row_number))

    def warning(self, message, row_number=None):
        self.warnings.append(describe(message, row_number))

    def has_errors(self):
        return bool(self.errors)


def describe(message, row_number=None):
    """Put the row number in front, so the linguist can jump straight to it.

    Example: describe("ud_id is missing", 145) -> "row 145: ud_id is missing"
    """
    if row_number is None:
        return message

    return f"row {row_number}: {message}"


def shorten(messages):
    """Indent the messages, cutting the list off when it gets absurdly long."""
    lines = [f"  {message}" for message in messages[:MAX_REPORTED_PROBLEMS]]

    hidden = len(messages) - MAX_REPORTED_PROBLEMS
    if hidden > 0:
        lines.append(f"  ... and {hidden} more of the same kind")

    return lines


class DataProblems(Exception):
    """Raised instead of importing a file that has errors in it."""

    def __init__(self, path, errors, warnings=()):
        self.path = path
        self.errors = errors
        self.warnings = list(warnings)
        super().__init__(f"{len(errors)} problems in {path}")

    def report(self):
        """The lines to show the person who has to fix the file.

        The warnings are listed as well: they do not stop the import on their
        own, but somebody correcting the file may as well see them now instead
        of on the next run.
        """
        lines = [
            f"{len(self.errors)} problems found in {self.path} "
            "— nothing was imported"
        ]
        lines += shorten(self.errors)

        if self.warnings:
            lines.append('Also worth checking:')
            lines += shorten(self.warnings)

        lines.append('Please correct the file and run the import again.')
        return lines
