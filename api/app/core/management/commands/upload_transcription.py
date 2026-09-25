from django.core.management.base import BaseCommand, CommandError

from core.processing.exporting.after_import import EXPORT_FAILED_ADVICE, export_texts_for_server
from core.processing.importing.problems import DataProblems
from core.processing.importing.tokens import import_tokens
from helpers.logger import logger


class Command(BaseCommand):
    help = (
        'Import an annotated text into sentences and tokens. '
        'The file is checked first: if anything is wrong with it, nothing is '
        'imported and every problem found is listed. '
        'Run import_texts and import_speakers first, so that the text and its '
        'speakers already exist. The file may be exactly as the linguists send '
        'it: the text is found by its title and the speakers by their names.'
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
        parser.add_argument(
            '--text',
            help=(
                'The text_id of the text, e.g. panov_pechalbari_1936. Needed only '
                'when the title in the file belongs to more than one text.'
            ),
        )

    def handle(self, *args, **options):
        path = options['annotations']

        try:
            summary, warnings = import_tokens(
                path,
                allow_unknown_speakers=options['allow_unknown_speakers'],
                text_id=options['text'],
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

        logger.info(
            f"{summary['text_id']}: {summary['sentences']} sentences, "
            f"{summary['tokens']} tokens imported."
        )

        try:
            export_texts_for_server([summary['text_id']])
        except OSError as error:
            logger.error(str(error))
            raise CommandError(EXPORT_FAILED_ADVICE)
