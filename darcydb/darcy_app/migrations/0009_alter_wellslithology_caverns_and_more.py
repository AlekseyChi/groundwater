# Generated by Django 4.1.10 on 2023-08-22 02:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("darcy_app", "0008_historicalwellslithology_wellslithology"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wellslithology",
            name="caverns",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="caverns",
                to="darcy_app.dictentities",
                verbose_name="Кавернозность",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="cement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="cement",
                to="darcy_app.dictentities",
                verbose_name="Состав цемента",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="color",
                to="darcy_app.dictentities",
                verbose_name="Цвет",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="composition",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="composition",
                to="darcy_app.dictentities",
                verbose_name="Гранулометрический состав",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="fracture",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="fracture",
                to="darcy_app.dictentities",
                verbose_name="Трещиноватость",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="inclusions",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="inclusions",
                to="darcy_app.dictentities",
                verbose_name="Включения",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="mineral",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="mineral_cmspt",
                to="darcy_app.dictentities",
                verbose_name="Минеральный состав",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="secondary_change",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="secondary_change",
                to="darcy_app.dictentities",
                verbose_name="Вторичные изменения",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="structure",
                to="darcy_app.dictentities",
                verbose_name="Структура",
            ),
        ),
        migrations.AlterField(
            model_name="wellslithology",
            name="weathering",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="weathering",
                to="darcy_app.dictentities",
                verbose_name="Степень выветрелости",
            ),
        ),
    ]
