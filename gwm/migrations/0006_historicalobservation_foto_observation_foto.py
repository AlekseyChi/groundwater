# Generated by Django 4.0.7 on 2022-09-16 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gwm', '0005_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='foto',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gwm.foto', verbose_name='фотоотчет'),
        ),
        migrations.AddField(
            model_name='observation',
            name='foto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gwm.foto', verbose_name='фотоотчет'),
        ),
    ]
