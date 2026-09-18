from django.core.management.base import BaseCommand, CommandError

from core.processing.importing.tokens import import_tokens


class Command(BaseCommand):
    help = (
        'Import an annotated text into sentences and tokens. '
        'Run import_texts and import_speakers first, so that the text and its '
        'speakers already exist.'
    )

    def add_arguments(self, parser):
        parser.add_argument('annotations', type=str, help='Path to the .xlsx or .csv file')

    def handle(self, *args, **options):
        path = options['annotations']
        try:
            summaries = import_tokens(path)
        except (ValueError, OSError) as error:
            raise CommandError(str(error))

        for summary in summaries:
            if summary['replaced_sentences']:
                self.stdout.write(
                    f"Replaced the {summary['replaced_sentences']} sentences "
                    f"already stored for {summary['text_id']}."
                )
            if summary['unknown_speakers']:
                self.stdout.write(self.style.WARNING(
                    'These speakers are not in the database, so their sentences '
                    'have no speaker: '
                    + ', '.join(summary['unknown_speakers'])
                    + '. Run import_speakers and import this file again.'
                ))
            self.stdout.write(self.style.SUCCESS(
                f"{summary['text_id']}: {summary['sentences']} sentences, "
                f"{summary['tokens']} tokens."
            ))
