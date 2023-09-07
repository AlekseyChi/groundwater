# Generated by Django 4.1.10 on 2023-09-07 00:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("darcy_app", "0018_alter_historicalwellsrate_time_measure_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalwellsconstruction",
            name="date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Дата установки"
            ),
        ),
        migrations.AlterField(
            model_name="wellsconstruction",
            name="date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Дата установки"
            ),
        ),
    ]
