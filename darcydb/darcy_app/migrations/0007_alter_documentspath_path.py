# Generated by Django 4.1.9 on 2023-07-05 12:05

import darcydb.darcy_app.models
import darcydb.darcy_app.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("darcy_app", "0006_alter_historicalwellswaterdepth_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentspath",
            name="path",
            field=models.FileField(
                storage=darcydb.darcy_app.storage_backends.YandexObjectStorage(),
                upload_to=darcydb.darcy_app.models.user_directory_path,
                verbose_name="Файл документа",
            ),
        ),
    ]
