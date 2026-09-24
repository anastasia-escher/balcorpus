import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_is_up = False
        while not db_is_up:
            try:
                # Looking up connections["default"] does not connect yet;
                # ensure_connection() is what actually talks to the database.
                connections["default"].ensure_connection()
                db_is_up = True
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
