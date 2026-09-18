import csv

from django.core.management.base import BaseCommand
from core.models import Sentence, Token, Speaker, Text
from helpers.logger import logger


CSV_COLUMNS = {
    'sentence_id': 0,
    'ud_id': 1,
    'source': 2,
    'diplomatic': 3,
    'lemma': 4,
    'ud_type_pos': 5,
    'pos_tag': 6,
    'ud_valency': 7,
    'head_id': 8,
    'ud_type': 9,
    'speaker': 10,
    'text_id': 11,
}


def value(row, column):
    return row[CSV_COLUMNS[column]].strip() if len(row) > CSV_COLUMNS[column] else ''


def get_speaker(raw_speaker):
    details = {}
    for part in raw_speaker.split('|'):
        if '=' in part:
            key, raw_value = part.split('=', 1)
            details[key] = raw_value

    speaker_id = details.get('Speaker', '').strip()
    if not speaker_id:
        return None

    full_name = details.get('FullName', speaker_id).replace('_', ' ').strip() or speaker_id
    speaker, _ = Speaker.objects.update_or_create(
        speaker_id=speaker_id,
        defaults={'full_name': full_name},
    )
    return speaker


def process_rows(rows):
    current_text_id = None
    imported_tokens = 0

    for row in rows:
        if not value(row, 'sentence_id'):
            continue

        raw_text_id = value(row, 'text_id')
        if raw_text_id:
            current_text_id = int(raw_text_id)
        if current_text_id is None:
            raise ValueError('The first token row must specify text_id.')

        text, _ = Text.objects.get_or_create(
            text_id=current_text_id,
            defaults={'text_name': f'Text {current_text_id}'},
        )
        if not text.text_name:
            text.text_name = f'Text {current_text_id}'
            text.save(update_fields=['text_name'])
        speaker = get_speaker(value(row, 'speaker'))
        sentence, created = Sentence.objects.get_or_create(
            text=text,
            sentence_id=int(value(row, 'sentence_id')),
            defaults={'speaker': speaker},
        )
        if not created and speaker and sentence.speaker_id != speaker.id:
            sentence.speaker = speaker
            sentence.save(update_fields=['speaker'])

        Token.objects.update_or_create(
            sentence=sentence,
            ud_id=int(value(row, 'ud_id')),
            defaults={
                'source': value(row, 'source'),
                'diplomatic': value(row, 'diplomatic'),
                'lemma': value(row, 'lemma'),
                'ud_type_pos': value(row, 'ud_type_pos'),
                'pos_tag': value(row, 'pos_tag'),
                'ud_valency': value(row, 'ud_valency'),
                'pos_tag2': value(row, 'head_id'),
                'ud_type': value(row, 'ud_type'),
            },
        )
        imported_tokens += 1

    return imported_tokens

class Command(BaseCommand):
    help = 'Import annotated sentences from CSV and update DB'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['csv_file']
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # The source has two columns both named POS_Tag.
            imported_tokens = process_rows(reader)
        self.stdout.write(self.style.SUCCESS(f'Imported {imported_tokens} tokens from {file_path}.'))
