from core.models import Global
from django.core.management import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Uploads sample data (including Russian fields) for the Shwa Functional Matrix."

    @transaction.atomic
    def handle(self, *args, **options):
        pass
        # if not Global.objects.exists():
        #     # Create a new Global instance
        #     global_instance = Global.objects.create(
        #         name="Shwa Functional Matrix",
        #         description="A comprehensive matrix for analyzing Shwa language features.",
        #         version="1.0",
        #         created_by="admin",
        #     )
        #     self.stdout.write(self.style.SUCCESS(f"Global instance created: {global_instance}"))