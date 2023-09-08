# Generated by Django 4.1.10 on 2023-08-23 23:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("darcy_app", "0010_alter_wellssample_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="License",
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
                    "created",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "modified",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        default="ufo",
                        editable=False,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "remote_addr",
                    models.GenericIPAddressField(blank=True, editable=False, null=True),
                ),
                ("extra", models.JSONField(blank=True, editable=False, null=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "name",
                    models.CharField(
                        max_length=11, unique=True, verbose_name="Номер лицензии"
                    ),
                ),
                (
                    "date_start",
                    models.DateField(
                        blank=True, null=True, verbose_name="Дата выдачи лицензии"
                    ),
                ),
                ("date_end", models.DateField(verbose_name="Дата окончания лицензии")),
                (
                    "comments",
                    models.TextField(blank=True, null=True, verbose_name="Примечание"),
                ),
                ("gw_purpose", models.TextField(verbose_name="Целевое назначение ПВ")),
                (
                    "department",
                    models.ForeignKey(
                        db_column="department",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="darcy_app.dictdocorganizations",
                        verbose_name="Орган, выдавший лицензию",
                    ),
                ),
                (
                    "last_user",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Лицензия",
                "verbose_name_plural": "Лицензии",
                "db_table": "license",
            },
        ),
        migrations.AlterModelOptions(
            name="wellsdrilleddata",
            options={
                "ordering": ("-date_end", "well"),
                "verbose_name": "Данные бурения",
                "verbose_name_plural": "Данные бурения",
            },
        ),
        migrations.AlterUniqueTogether(
            name="wellsdrilleddata",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="historicalwellsdrilleddata",
            name="date",
        ),
        migrations.AddField(
            model_name="historicalwellsdrilleddata",
            name="date_end",
            field=models.DateField(
                default="1970-01-01", verbose_name="Дата окончания бурения"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalwellsdrilleddata",
            name="date_start",
            field=models.DateField(
                default="1970-01-01", verbose_name="Дата начала бурения"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalwellsdrilleddata",
            name="organization",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Буровая организация",
            ),
        ),
        migrations.AddField(
            model_name="historicalwellsefw",
            name="vessel_capacity",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Ёмкость мерного сосуда, м3"
            ),
        ),
        migrations.AddField(
            model_name="historicalwellsefw",
            name="vessel_time",
            field=models.TimeField(
                blank=True, null=True, verbose_name="Время наполнения ёмкости, сек"
            ),
        ),
        migrations.AddField(
            model_name="wellsdrilleddata",
            name="date_end",
            field=models.DateField(
                default="1970-01-01", verbose_name="Дата окончания бурения"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wellsdrilleddata",
            name="date_start",
            field=models.DateField(
                default="1970-01-01", verbose_name="Дата начала бурения"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wellsdrilleddata",
            name="organization",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Буровая организация",
            ),
        ),
        migrations.AddField(
            model_name="wellsefw",
            name="vessel_capacity",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Ёмкость мерного сосуда, м3"
            ),
        ),
        migrations.AddField(
            model_name="wellsefw",
            name="vessel_time",
            field=models.TimeField(
                blank=True, null=True, verbose_name="Время наполнения ёмкости, сек"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="wellsdrilleddata",
            unique_together={("well", "date_end")},
        ),
        migrations.CreateModel(
            name="WellsGeophysics",
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
                    "created",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "modified",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        default="ufo",
                        editable=False,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "remote_addr",
                    models.GenericIPAddressField(blank=True, editable=False, null=True),
                ),
                ("extra", models.JSONField(blank=True, editable=False, null=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("date", models.DateField(verbose_name="Дата производства работ")),
                (
                    "organization",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Наименование организации",
                    ),
                ),
                (
                    "researches",
                    models.TextField(verbose_name="Геофизические исследования"),
                ),
                (
                    "conclusion",
                    models.TextField(verbose_name="Результаты исследований"),
                ),
                (
                    "doc",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="darcy_app.documents",
                        verbose_name="Документ",
                    ),
                ),
                (
                    "last_user",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "well",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="darcy_app.wells",
                        verbose_name="Номер скважины",
                    ),
                ),
            ],
            options={
                "verbose_name": "Геофизические исследования",
                "verbose_name_plural": "Геофизические исследования",
                "db_table": "wells_geophysics",
                "ordering": ("-date", "well"),
                "unique_together": {("well", "date")},
            },
        ),
        migrations.CreateModel(
            name="WaterUsers",
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
                    "created",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "modified",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        default="ufo",
                        editable=False,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "remote_addr",
                    models.GenericIPAddressField(blank=True, editable=False, null=True),
                ),
                ("extra", models.JSONField(blank=True, editable=False, null=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "name",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="Водопользователь"
                    ),
                ),
                (
                    "position",
                    models.TextField(blank=True, null=True, verbose_name="Адрес"),
                ),
                (
                    "last_user",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Водопользователь",
                "verbose_name_plural": "Водопользователи",
                "db_table": "water_users",
            },
        ),
        migrations.CreateModel(
            name="LicenseToWells",
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
                    "created",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "modified",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        default="ufo",
                        editable=False,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "remote_addr",
                    models.GenericIPAddressField(blank=True, editable=False, null=True),
                ),
                ("extra", models.JSONField(blank=True, editable=False, null=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "last_user",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "license",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="darcy_app.license",
                        verbose_name="Лицензия",
                    ),
                ),
                (
                    "well",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="darcy_app.wells",
                        verbose_name="Номер скважины",
                    ),
                ),
            ],
            options={
                "verbose_name": "Связь скважины с лицензией",
                "verbose_name_plural": "Связи скважин с лицензиями",
                "db_table": "license_to_wells",
                "unique_together": {("well", "license")},
            },
        ),
        migrations.CreateModel(
            name="HistoricalWellsGeophysics",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "modified",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        default="ufo",
                        editable=False,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "remote_addr",
                    models.GenericIPAddressField(blank=True, editable=False, null=True),
                ),
                ("extra", models.JSONField(blank=True, editable=False, null=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("date", models.DateField(verbose_name="Дата производства работ")),
                (
                    "organization",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Наименование организации",
                    ),
                ),
                (
                    "researches",
                    models.TextField(verbose_name="Геофизические исследования"),
                ),
                (
                    "conclusion",
                    models.TextField(verbose_name="Результаты исследований"),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "doc",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="darcy_app.documents",
                        verbose_name="Документ",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "last_user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "well",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="darcy_app.wells",
                        verbose_name="Номер скважины",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Геофизические исследования",
                "verbose_name_plural": "historical Геофизические исследования",
                "db_table": "wells_geophysics_history",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="DictEquipment",
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
                    "created",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "modified",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        default="ufo",
                        editable=False,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "remote_addr",
                    models.GenericIPAddressField(blank=True, editable=False, null=True),
                ),
                ("extra", models.JSONField(blank=True, editable=False, null=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("name", models.CharField(max_length=250, verbose_name="Название")),
                ("brand", models.CharField(max_length=250, verbose_name="Марка")),
                (
                    "last_user",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "typo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="darcy_app.dictentities",
                        verbose_name="Тип оборудования",
                    ),
                ),
            ],
            options={
                "verbose_name": "Словарь оборудования",
                "verbose_name_plural": "Словарь обородувания",
                "db_table": "dict_equipment",
            },
        ),
        migrations.RemoveField(
            model_name="wellsdrilleddata",
            name="date",
        ),
        migrations.AddField(
            model_name="historicalwellsefw",
            name="level_meter",
            field=models.ForeignKey(
                blank=True,
                db_column="level_meter",
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="darcy_app.dictequipment",
                verbose_name="Уровнемер",
            ),
        ),
        migrations.AddField(
            model_name="wellsefw",
            name="level_meter",
            field=models.ForeignKey(
                blank=True,
                db_column="level_meter",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="level_meter",
                to="darcy_app.dictequipment",
                verbose_name="Уровнемер",
            ),
        ),
        migrations.AlterField(
            model_name="historicalwellsefw",
            name="pump_type",
            field=models.ForeignKey(
                blank=True,
                db_column="pump_type",
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="darcy_app.dictequipment",
                verbose_name="Тип водоподъемного оборудования",
            ),
        ),
        migrations.AlterField(
            model_name="wellsefw",
            name="pump_type",
            field=models.ForeignKey(
                db_column="pump_type",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="pump_type",
                to="darcy_app.dictequipment",
                verbose_name="Тип водоподъемного оборудования",
            ),
        ),
        migrations.DeleteModel(
            name="DictPump",
        ),
    ]