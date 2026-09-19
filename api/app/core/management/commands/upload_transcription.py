from django.core.management.base import BaseCommand, CommandError

from core.processing.exporting.after_import import export_texts_for_server
from core.processing.importing.problems import DataProblems
from core.processing.importing.tokens import import_tokens
from helpers.logger import logger


class Command(BaseCommand):
    help = (
        'Import an annotated text into sentences and tokens. '
        'The file is checked first: if anything is wrong with it, nothing is '
        'imported and every problem found is listed. '
        'Run import_texts and import_speakers first, so that the text and its '
        'speakers already exist.'
    )

    def add_arguments(self, parser):
        parser.add_argument('annotations', type=str, help='Path to the .xlsx or .csv file')
        parser.add_argument(
            '--allow-unknown-speakers',
            action='store_true',
            help=(
                'Import even though the file names speakers that are not in the '
                'database. Their sentences will have no speaker.'
            ),
        )

    def handle(self, *args, **options):
        path = options['annotations']

        try:
            summaries, warnings = import_tokens(
                path, allow_unknown_speakers=options['allow_unknown_speakers']
            )
        except DataProblems as problems:
            for line in problems.report():
                logger.error(line)
            raise CommandError(f'{path} was not imported.')
        except (ValueError, OSError) as error:
            logger.error(str(error))
            raise CommandError(f'{path} could not be read.')

        for warning in warnings:
            logger.warning(warning)

        for summary in summaries:
            logger.info(
                f"{summary['text_id']}: {summary['sentences']} sentences, "
                f"{summary['tokens']} tokens imported."
            )

        # One file may carry more than one text, so every text it touched is
        # written out, not just the first.
        export_texts_for_server(summary['text_id'] for summary in summaries)
