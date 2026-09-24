from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_remove_speaker_education_remove_speaker_variety_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="speaker",
            name="show_metadata",
            field=models.BooleanField(default=True),
        ),
    ]
