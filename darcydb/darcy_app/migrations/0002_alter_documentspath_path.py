# Generated by Django 4.1.9 on 2023-06-07 15:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("darcy_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentspath",
            name="path",
            field=models.FileField(upload_to="", verbose_name="Файл документа"),
        ),
    ]
