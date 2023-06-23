# from django.contrib.contenttypes.models import ContentType
from import_export import resources
from import_export.fields import Field

from .models import WellsRegime

# , WellsWaterDepth, Wells
# from import_export.widgets import ForeignKeyWidget


class WellsRegimeResource(resources.ModelResource):
    water_depth = Field(
        column_name="water_depth",
    )

    # def after_save_instance(self, instance, **kwargs):
    #     well = instance.well
    #     date = instance.date
    #     wells_regime_content_type = ContentType.objects.get_for_model(WellsRegime)
    #     content_type = wells_regime_content_type.id
    #     object_id = instance.id
    #     water_depth = instance.water_depth

    class Meta:
        model = WellsRegime
        fields = ("id", "well", "date")
        import_id_fields = ("well", "date")
