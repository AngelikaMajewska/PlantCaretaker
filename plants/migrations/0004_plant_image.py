# Generated by Django 5.2 on 2025-04-26 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plants", "0003_remove_plant_pot_size_alter_plant_light"),
    ]

    operations = [
        migrations.AddField(
            model_name="plant",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="plant_images/"),
        ),
    ]
