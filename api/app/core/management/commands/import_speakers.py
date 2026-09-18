from django.core.management.base import BaseCommand, CommandError

from core.processing.importing.speakers import import_speakers


class Command(BaseCommand):
    help = 'Import the metadata table describing the speakers and authors.'

    def add_arguments(self, parser):
        parser.add_argument('table', type=str, help='Path to the .csv or .xlsx file')

    def handle(self, *args, **options):
        path = options['table']
        try:
            summary = import_speakers(path)
        except (ValueError, OSError) as error:
            raise CommandError(str(error))

        self.stdout.write(self.style.SUCCESS(
            f"{summary['created']} speakers created, {summary['updated']} updated "
            f"from {path}."
        ))
