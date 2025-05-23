# Generated by Django 5.2 on 2025-04-27 16:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plants", "0004_plant_image"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Comments",
            new_name="PlantDetailComments",
        ),
        migrations.CreateModel(
            name="UserNotes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("note", models.TextField()),
                ("date", models.DateField(auto_now_add=True)),
                (
                    "plant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="plants.plant"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OwnedPlants",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "plant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="plants.plant"
                    ),
                ),
            ],
            options={
                "unique_together": {("owner", "plant")},
            },
        ),
        migrations.CreateModel(
            name="WishList",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "plant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="plants.plant"
                    ),
                ),
            ],
            options={
                "unique_together": {("owner", "plant")},
            },
        ),
    ]
