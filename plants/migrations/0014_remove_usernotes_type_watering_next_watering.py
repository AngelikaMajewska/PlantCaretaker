# Generated by Django 5.2 on 2025-05-03 09:33

import plants.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plants", "0013_airating_note"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usernotes",
            name="type",
        ),
        migrations.AddField(
            model_name="watering",
            name="next_watering",
            field=models.DateField(default=None),
        ),
    ]
