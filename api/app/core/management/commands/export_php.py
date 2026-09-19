from django.core.management.base import BaseCommand, CommandError

from core.models import Sentence, Text
from core.processing.exporting.after_import import (
    export_metadata_for_server,
    export_texts_for_server,
)
from core.processing.exporting.php_export import (
    DEFAULT_OUTPUT_FOLDER,
    annotated_text_ids,
)
from helpers.logger import logger


class Command(BaseCommand):
    help = (
        'Write the corpus out as the CSV files the PHP server loads. '
        'Every import command already ends with this for what it changed, so '
        'this is for writing the whole corpus again: after restoring a backup, '
        'or when the folder has been emptied. '
        'The metadata is written whole; the annotation gets one file per text.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=DEFAULT_OUTPUT_FOLDER,
            help=f'Folder to write into (default: {DEFAULT_OUTPUT_FOLDER})',
        )
        parser.add_argument(
            '--text',
            type=str,
            help=(
                'Write only this one text, e.g. --text panov_pechalbari_1936. '
                'The metadata is then left as it is.'
            ),
        )

    def handle(self, *args, **options):
        output_folder = options['output']
        text_id = options['text']

        if text_id:
            self.export_one_text(text_id, output_folder)
            return

        export_metadata_for_server(output_folder)
        summaries = export_texts_for_server(annotated_text_ids(), output_folder)

        if not summaries:
            logger.warning(
                'No text carries an annotation yet, so only the metadata was written.'
            )

    def export_one_text(self, text_id, output_folder):
        """Write the two annotation files of a single text."""
        if not Text.objects.filter(text_id=text_id).exists():
            raise CommandError(f'The corpus has no text called {text_id}.')

        # Writing the empty files would be worse than writing nothing: the
        # loader on the server replaces what it holds for a text with what the
        # file contains, so an empty file would erase an annotation that is
        # already there.
        if not Sentence.objects.filter(text_id=text_id).exists():
            raise CommandError(
                f'{text_id} has no annotation imported, so there is nothing to '
                'write. Import it first: manage.py upload_transcription <file>.'
            )

        export_texts_for_server([text_id], output_folder)
