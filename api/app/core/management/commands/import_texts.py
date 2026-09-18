from django.core.management.base import BaseCommand, CommandError

from core.processing.importing.texts import import_texts


class Command(BaseCommand):
    help = 'Import the metadata table describing the corpus documents.'

    def add_arguments(self, parser):
        parser.add_argument('table', type=str, help='Path to the .csv or .xlsx file')

    def handle(self, *args, **options):
        path = options['table']
        try:
            summary = import_texts(path)
        except (ValueError, OSError) as error:
            raise CommandError(str(error))

        self.stdout.write(self.style.SUCCESS(
            f"{summary['created']} texts created, {summary['updated']} updated "
            f"from {path}."
        ))
