# Generated by Django 4.1.9 on 2023-06-07 21:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("darcy_app", "0002_alter_documentspath_path"),
    ]

    operations = [
        migrations.AddField(
            model_name="documents",
            name="authors",
            field=models.TextField(blank=True, null=True, verbose_name="Авторы"),
        ),
        migrations.AddField(
            model_name="historicaldocuments",
            name="authors",
            field=models.TextField(blank=True, null=True, verbose_name="Авторы"),
        ),
        migrations.AlterField(
            model_name="dictentities",
            name="entity",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="darcy_app.entities",
                verbose_name="Справочник",
            ),
        ),
        migrations.AlterField(
            model_name="dictentities",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Значение"),
        ),
    ]
