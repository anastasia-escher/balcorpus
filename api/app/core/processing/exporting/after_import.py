"""Writing the server's files as the last step of an import.

An import that is not followed by an export leaves the two out of step: the
database holds the new data while php_ready still holds the old, and the
difference is invisible until the wrong files have been copied to the server.
So every import command ends here, and nobody has to remember a second
command.

The functions log what they wrote, because that is the only sign the person
running the import gets that the files for the server were refreshed.
"""

from helpers.logger import logger

from .php_export import DEFAULT_OUTPUT_FOLDER, export_annotation, export_metadata

# What to tell the person running an import when the database took the data
# but the files for the server could not be written. Without it the error
# would read like a failed import, and they would run it again for nothing.
EXPORT_FAILED_ADVICE = (
    'The data is in the database, but the files for the server could not be '
    'written. Fix the problem above, then write them with: manage.py export_php'
)


def export_metadata_for_server(output_folder=DEFAULT_OUTPUT_FOLDER):
    """Write the three metadata files and say what went into them.

    They are rewritten whole every time. A hundred texts and their authors
    take no measurable time, and rewriting all three keeps them consistent
    with each other.
    """
    summary = export_metadata(output_folder)

    logger.info(
        f"For the server: {summary['speakers']} speakers, {summary['texts']} texts, "
        f"{summary['text_authors']} author links written to {output_folder}"
    )

    return summary


def export_texts_for_server(text_ids, output_folder=DEFAULT_OUTPUT_FOLDER):
    """Write the annotation files of the given texts, one pair per text.

    ``text_ids`` is any iterable of slugs, e.g.
    ['panov_pechalbari_1936', 'vasil_iljoski_corbadji_1937'].
    """
    summaries = []

    for text_id in text_ids:
        summary = export_annotation(text_id, output_folder)
        summaries.append(summary)

        logger.info(
            f"For the server: {text_id}, {summary['sentences']} sentences and "
            f"{summary['tokens']} tokens written to {output_folder}"
        )

    return summaries
