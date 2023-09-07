# Generated by Django 4.1.10 on 2023-09-07 12:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("darcy_app", "0019_alter_historicalwellsconstruction_date_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="documents",
            unique_together={("name", "typo", "content_type", "object_id")},
        ),
        migrations.AlterUniqueTogether(
            name="wellsconstruction",
            unique_together={
                (
                    "well",
                    "date",
                    "depth_from",
                    "construction_type",
                    "depth_till",
                    "diameter",
                )
            },
        ),
    ]
