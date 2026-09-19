from django.core.management.base import BaseCommand, CommandError

from core.processing.exporting.after_import import export_metadata_for_server
from core.processing.importing.problems import DataProblems
from core.processing.importing.speakers import import_speakers
from helpers.logger import logger


class Command(BaseCommand):
    help = (
        'Import the metadata table describing the speakers and authors. '
        'The table is checked first: if anything is wrong with it, nothing is '
        'imported and every problem found is listed.'
    )

    def add_arguments(self, parser):
        parser.add_argument('table', type=str, help='Path to the .csv or .xlsx file')

    def handle(self, *args, **options):
        path = options['table']

        try:
            summary, warnings = import_speakers(path)
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
            f"{summary['created']} speakers created, {summary['updated']} updated."
        )

        export_metadata_for_server()
