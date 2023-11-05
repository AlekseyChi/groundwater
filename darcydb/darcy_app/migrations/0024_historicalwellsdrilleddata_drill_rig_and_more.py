# Generated by Django 4.1.10 on 2023-09-09 11:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("darcy_app", "0023_alter_attachments_img"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalwellsdrilleddata",
            name="drill_rig",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Буровая установка"
            ),
        ),
        migrations.AddField(
            model_name="historicalwellsdrilleddata",
            name="drill_type",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Тип бурения"
            ),
        ),
        migrations.AddField(
            model_name="wellsdrilleddata",
            name="drill_rig",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Буровая установка"
            ),
        ),
        migrations.AddField(
            model_name="wellsdrilleddata",
            name="drill_type",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Тип бурения"
            ),
        ),
    ]
