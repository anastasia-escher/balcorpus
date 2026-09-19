from django.core.management.base import BaseCommand, CommandError

from core.models import Sentence, Text
from core.processing.exporting.php_export import export_annotation, export_everything
from helpers.logger import logger

# Where the files land unless the caller says otherwise.  The project's ./data
# folder is mounted as /data inside the container, so this is data/php_ready,
# next to data/input where the linguists' files arrive.
DEFAULT_OUTPUT_FOLDER = '/data/php_ready'


class Command(BaseCommand):
    help = (
        'Write the corpus out as the CSV files the PHP server loads. '
        'Run it after importing, so that what leaves for the server is what '
        'the checks have already passed. '
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
                'Its metadata is not rewritten, so use this after re-importing '
                'an annotation that is already in the corpus.'
            ),
        )

    def handle(self, *args, **options):
        output_folder = options['output']
        text_id = options['text']

        if text_id:
            self.export_one_text(text_id, output_folder)
            return

        metadata, annotations = export_everything(output_folder)

        logger.info(
            f"{metadata['speakers']} speakers, {metadata['texts']} texts, "
            f"{metadata['text_authors']} author links written."
        )

        for summary in annotations:
            logger.info(
                f"{summary['text_id']}: {summary['sentences']} sentences, "
                f"{summary['tokens']} tokens written."
            )

        if not annotations:
            logger.warning('No text carries an annotation yet, so only the metadata was written.')

        logger.info(f'The files for the server are in {output_folder}')

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

        summary = export_annotation(text_id, output_folder)

        logger.info(
            f"{text_id}: {summary['sentences']} sentences, "
            f"{summary['tokens']} tokens written to {output_folder}"
        )
