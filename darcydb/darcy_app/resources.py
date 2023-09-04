from django.contrib.contenttypes.models import ContentType
from import_export import fields, resources
from import_export.widgets import DateWidget, ForeignKeyWidget

from .models import Wells, WellsRegime, WellsWaterDepth


class WellsRegimeResource(resources.ModelResource):
    well = fields.Field(column_name="well", attribute="well", widget=ForeignKeyWidget(Wells, "id"))
    date = fields.Field(column_name="date", attribute="date", widget=DateWidget("%Y-%m-%d"))
    water_depth = fields.Field(column_name="water_depth")

    class Meta:
        model = WellsRegime
        fields = (
            "well",
            "date",
        )
        import_id_fields = (
            "well",
            "date",
        )

    def before_save_instance(self, instance, using_transactions, dry_run):
        if not instance.id:
            last_record = WellsRegime.objects.order_by("id").last()
            if last_record:
                instance.id = last_record.id + 1
            else:
                instance.id = 1

    def after_import_row(self, row, row_result, **kwargs):
        instance = row_result.object_id
        if instance:  # check if the instance was actually created
            water_depth_value = row.get("water_depth")
            if water_depth_value is not None:
                WellsWaterDepth.objects.create(
                    content_type=ContentType.objects.get_for_model(WellsRegime),
                    object_id=instance,
                    time_measure="00:00",
                    water_depth=water_depth_value,
                )
