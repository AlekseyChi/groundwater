# Generated by Django 4.0.7 on 2022-09-16 11:58

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='geolinkVZU',
            fields=[
                ('code', models.BigIntegerField(primary_key=True, serialize=False)),
                ('article', models.TextField(verbose_name='full name')),
                ('header', models.CharField(max_length=255, verbose_name='short name')),
            ],
            options={
                'verbose_name': 'Справочник ВЗУ (read only!)',
                'verbose_name_plural': 'Справочник ВЗУ (read only!)',
                'db_table': '"Kursk"."00010"',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Kursk_wells',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('geom', django.contrib.gis.db.models.fields.PointField(help_text='точки', srid=4326, verbose_name='геометрия точки (xyz)')),
                ('fid', models.CharField(blank=True, max_length=255, null=True, verbose_name='fid')),
                ('Well_Name', models.CharField(blank=True, max_length=255, null=True, verbose_name='номер')),
                ('Well_type', models.CharField(blank=True, max_length=255, null=True, verbose_name='тип')),
                ('Aq_Name', models.CharField(blank=True, max_length=255, null=True, verbose_name='геология текст')),
                ('Aq_index', models.CharField(blank=True, max_length=255, null=True, verbose_name='геология индекс')),
                ('MPV', models.CharField(blank=True, max_length=255, null=True, verbose_name='МПВ')),
                ('VZU', models.CharField(blank=True, max_length=255, null=True, verbose_name='ВЗУ')),
                ('Owner', models.CharField(blank=True, max_length=255, null=True, verbose_name='owner')),
                ('RGF_ID', models.BigIntegerField(blank=True, null=True, verbose_name='RGF ID')),
                ('Well_cond', models.CharField(blank=True, max_length=255, null=True, verbose_name='состояние')),
                ('Intake_A', models.FloatField(blank=True, null=True, verbose_name='A')),
                ('Intake_B', models.FloatField(blank=True, null=True, verbose_name='B')),
                ('Intake_C1', models.FloatField(blank=True, null=True, verbose_name='C1')),
                ('GVK', models.CharField(blank=True, max_length=255, null=True, verbose_name='№ГВК')),
                ('prim', models.TextField(blank=True, null=True, verbose_name='примечание')),
            ],
            options={
                'verbose_name': 'Poi ВЗУ Курск',
                'verbose_name_plural': 'Poi ВЗУ Курск',
                'db_table': 'kursk_well',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Spatial',
            fields=[
                ('srid', models.IntegerField(primary_key=True, serialize=False, verbose_name='srid')),
                ('auth_name', models.CharField(max_length=256, verbose_name='auth_name')),
                ('auth_srid', models.IntegerField(verbose_name='auth_srid')),
                ('srtext', models.TextField(verbose_name='srtext')),
                ('proj4text', models.TextField(verbose_name='proj4text')),
            ],
            options={
                'verbose_name': 'cистему координат',
                'verbose_name_plural': 'cистемы координат (spatial_ref_sys - read only!)',
                'db_table': 'spatial_ref_sys',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='spr_geol_index',
            fields=[
                ('code', models.BigIntegerField(primary_key=True, serialize=False)),
                ('article', models.TextField(verbose_name='full name')),
                ('header', models.CharField(max_length=255, unique=True, verbose_name='short name')),
            ],
            options={
                'verbose_name': 'Справочник Геологический индекс (read only!)',
                'verbose_name_plural': 'Справочник Геологический индекс (read only!)',
                'db_table': '"Kursk"."00002"',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='topo250mRus',
            fields=[
                ('gid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4284, verbose_name='планшет')),
            ],
            options={
                'verbose_name': 'номенклатурные номера листов 25000 (read only!)',
                'verbose_name_plural': '1:25000 (read only!)',
                'db_table': 'topo250m-rus',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='topo500mRus',
            fields=[
                ('gid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4284, verbose_name='планшет')),
            ],
            options={
                'verbose_name': 'номенклатурные номера листов 50000 (read only!)',
                'verbose_name_plural': '1:50000 (read only!)',
                'db_table': 'topo500m-rus',
                'managed': False,
            },
        ),
    ]
