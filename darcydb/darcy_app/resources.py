# from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from import_export import fields, resources
from import_export.widgets import DateWidget  # ForeignKeyWidget

from .models import (
    AquiferCodes,
    Attachments,
    Balance,
    ChemCodes,
    DictDocOrganizations,
    DictEntities,
    DictEquipment,
    Documents,
    Entities,
    Fields,
    Intakes,
    License,
    LicenseToWells,
    WaterUsers,
    WaterUsersChange,
    Wells,
    WellsAquiferUsage,
    WellsChem,
    WellsCondition,
    WellsDepth,
    WellsDrilledData,
    WellsEfw,
    WellsGeophysics,
    WellsLithology,
    WellsLugHeight,
    WellsRate,
    WellsRegime,
    WellsSample,
    WellsTemperature,
    WellsWaterDepth,
)

__all__ = [
    "FieldsResource",
    "BalanceResource",
    "WellsEfwResource",
    "WellResource",
    "DocumentsResource",
    "LicenseResource",
    "LicenseToWellsResource",
    "WellsSampleResource",
    "WaterUsersResouce",
    "IntakesResource",
    "DictEntitiesResource",
    "EntitiesResource",
    "WellsRegimeResource",
    "WaterUsersChangeResource",
    "DictEquipmentResource",
    "WellsTemperatureResource",
    "WellsLithologyResource",
    "WellsGeophysicsResource",
    "WellsLugHeightResource",
    "WellsChemResource",
    "WellsAquiferUsageResource",
    "ChemCodesResource",
    "AquiferCodesResource",
    "DictDocOrganizationsResource",
    "WellsConditionResource",
    "WellsRateResource",
    "WellsDepthResource",
    "AttachmentsResource",
    "WellsDrilledDataResource",
]


class WellResource(resources.ModelResource):
    # docs = fields.Field()
    # attachments = fields.Field()

    # def dehydrate_docs(self, wells):
    #    wanted_model = ContentType.objects.get(model="Documents".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wells.id).pk  # noqa
    #    except Exception:
    #        return {}
    #
    # def dehydrate_attachments(self, wells):
    #    wanted_model = ContentType.objects.get(model="Attachments".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wells.id).pk  # noqa
    #    except Exception:
    #        return {}

    class Meta:
        model = Wells
        fields = ["id", "name", "typo", "head", "moved", "intake", "field", "geom", "extra"]


class WellsEfwResource(resources.ModelResource):
    """
    Resource for WellsEfw model for admin import-export data
    """

    # waterdepths = fields.Field()
    # lugs = fields.Field()
    #
    # def dehydrate_waterdepths(self, wellsefw):
    #    wanted_model = ContentType.objects.get(model="WellsWaterDepth".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellsefw.id).pk  # noqa
    #    except Exception:
    #        return {}
    #
    # def dehydrate_lugs(self, wellsefw):
    #    wanted_model = ContentType.objects.get(model="WellsWaterDepth".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellsefw.id).pk  # noqa
    #    except Exception:
    #        return {}

    class Meta:
        model = WellsEfw
        fields = [
            "id",
            "well",
            "date",
            "type_efw",
            "pump_type",
            "level_meter",
            "pump_depth",
            "method_measure",
            "rate_measure",
            "pump_time",
            "vessel_capacity",
            "vessel_time",
            "doc",
        ]


class BalanceResource(resources.ModelResource):
    """
    Resource for Balance model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = Balance
        fields = ["id", "aquifer", "typo", "a", "b", "c1", "c2", "content_type", "content_type__model", "object_id"]


class FieldsResource(resources.ModelResource):
    """
    Resource for Fields model for admin import-export data
    """

    # docs = fields.Field()
    # balances = fields.Field()
    #
    # def dehydrate_docs(self, instance):
    #    wanted_model = ContentType.objects.get(model="Documents".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=instance.id).pk  # noqa
    #    except Exception:
    #        return {}
    #
    # def dehydrate_balances(self, instance):
    #    wanted_model = ContentType.objects.get(model="Balance".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=instance.id).pk  # noqa
    #    except Exception:
    #        return {}

    class Meta:
        model = Fields
        fields = ["id", "field_name", "geom"]


class WellsSampleResource(resources.ModelResource):
    """
    Resource for WellsSample model for admin import-export data
    """

    # chemvalues = fields.Field()
    # attachments = fields.Field()
    #
    # def dehydrate_chemvalues(self, wellssample):
    #    wanted_model = ContentType.objects.get(model="WellsChem".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellssample.id).pk  # noqa
    #    except Exception:
    #        return {}
    #
    # def dehydrate_attachments(self, wellssample):
    #    wanted_model = ContentType.objects.get(model="Attachments".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellssample.id).pk  # noqa
    #    except Exception:
    #        return {}

    class Meta:
        model = WellsSample
        fields = ["id", "well", "date", "name", "doc"]


class LicenseToWellsResource(resources.ModelResource):
    """
    Resource for LicenseToWells model for admin import-export data
    """

    class Meta:
        model = LicenseToWells
        fields = ["id", "well", "license"]


class LicenseResource(resources.ModelResource):
    """
    Resource for License model for admin import-export data
    """

    date_start = fields.Field(column_name="date_start", attribute="date_start", widget=DateWidget("%Y-%m-%d"))
    date_end = fields.Field(column_name="date_end", attribute="date_end", widget=DateWidget("%Y-%m-%d"))
    # docs = fields.Field()

    # def dehydrate_docs(self, licence):
    #    wanted_model = ContentType.objects.get(model="Documents".lower()).model_class()
    #    # wanted_model = apps.get_model("Documents", licence.content_type.model)
    #    try:
    #        return wanted_model.objects.get(id=licence.id).pk  # noqa
    #    except Exception:
    #        return {}

    class Meta:
        model = License
        fields = ["id", "name", "department", "date_start", "date_end", "comments", "gw_purpose"]


class DocumentsResource(resources.ModelResource):
    """
    Resource for Documents model for admin import-export data
    """

    creation_date = fields.Field(column_name="creation_date", attribute="creation_date", widget=DateWidget("%Y-%m-%d"))

    class Meta:
        model = Documents
        fields = [
            "id",
            "name",
            "typo",
            "source",
            "org_executor",
            "org_customer",
            "creation_date",
            "creation_place",
            "number_rgf",
            "number_tfgi",
            "authors",
            "links",
        ]


class WaterUsersResouce(resources.ModelResource):
    """
    Resource for WaterUsers model for admin import-export data
    """

    class Meta:
        model = WaterUsers
        fields = ["id", "name", "position"]


class IntakesResource(resources.ModelResource):
    """
    Resource for Intakes model for admin import-export data
    """

    class Meta:
        model = Intakes
        fields = ["id", "intake_name", "geom"]


class DictEntitiesResource(resources.ModelResource):
    """
    Resource for DictEntities model for admin import-export data
    """

    class Meta:
        model = DictEntities
        fields = ["id", "name", "entity"]


class EntitiesResource(resources.ModelResource):
    """
    Resource for Entities model for admin import-export data
    """

    class Meta:
        model = Entities
        fields = ["id", "name"]


class WellsRegimeResource(resources.ModelResource):
    """
    Resource for WellsRegime model for admin import-export data
    """

    # well = fields.Field(column_name="well", attribute="well", widget=ForeignKeyWidget(Wells, "id"))
    date = fields.Field(column_name="date", attribute="date", widget=DateWidget("%Y-%m-%d"))
    # water_depth = fields.Field(column_name="water_depth")
    # water_depth = fields.Field()

    # def dehydrate_water_depth(self, wellsregime):
    #    wanted_model = ContentType.objects.get(model="WellsWaterDepth".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellsregime.object_id).pk
    #    except Exception:
    #        return {}

    class Meta:
        model = WellsRegime
        fields = ("id", "well", "date", "doc")
        # https://django-import-export.readthedocs.io/en/latest/advanced_usage.html#create-or-update-model-instances
        # import_id_fields = ("well", "date",) # ???
        # To define which fields identify an instance, use the import_id_fields meta attribute.
        # You can use this declaration to indicate which field (or fields) should be used to uniquely identify the row.
        # If you don’t declare import_id_fields, then a default declaration is used,
        # in which there is only one field: ‘id’.

    # def before_save_instance(self, instance, using_transactions, dry_run):
    #    if not instance.id:
    #        last_record = WellsRegime.objects.order_by("id").last()
    #        if last_record:
    #            instance.id = last_record.id + 1
    #        else:
    #            instance.id = 1

    # def after_import_row(self, row, row_result, **kwargs):
    #    instance = row_result.object_id
    #    if instance:  # check if the instance was actually created
    #        water_depth_value = row.get("water_depth")
    #        if water_depth_value is not None:
    #            WellsWaterDepth.objects.create(
    #                content_type=ContentType.objects.get_for_model(WellsRegime),
    #                object_id=instance,
    #                time_measure="00:00",
    #                water_depth=water_depth_value,
    #            )


class WaterUsersChangeResource(resources.ModelResource):
    """
    Resource for WaterUsersChange model for admin import-export data
    """

    date = fields.Field(column_name="date", attribute="date", widget=DateWidget("%Y-%m-%d"))

    class Meta:
        model = WaterUsersChange
        fields = ["id", "water_user", "date", "license"]


class DictEquipmentResource(resources.ModelResource):
    """
    Resource for DictEquipment model for admin import-export data
    """

    class Meta:
        model = DictEquipment
        fields = ["id", "typo", "name", "brand"]


class WellsTemperatureResource(resources.ModelResource):
    """
    Resource for WellsTemperature model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsTemperature
        fields = ["id", "time_measure", "temperature", "content_type", "content_type__model", "object_id"]


class WellsLithologyResource(resources.ModelResource):
    """
    Resource for WellsLithology model for admin import-export data
    """

    class Meta:
        model = WellsLithology
        fields = [
            "id",
            "well",
            "rock",
            "color",
            "composition",
            "structure",
            "mineral",
            "secondary_change",
            "cement",
            "fracture",
            "weathering",
            "caverns",
            "inclusions",
            "bot_elev",
            "doc",
        ]


class WellsGeophysicsResource(resources.ModelResource):
    """
    Resource for WellsGeophysics model for admin import-export data
    """

    # waterdepths = fields.Field()
    # attachments = fields.Field()
    #
    # def dehydrate_waterdepths(self, wellsgeophysics):
    #    wanted_model = ContentType.objects.get(model="WellsWaterDepth".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellsgeophysics.id).pk
    #    except Exception:
    #        return {}
    #
    # def dehydrate_attachments(self, wellsgeophysics):
    #    wanted_model = ContentType.objects.get(model="Attachments".lower()).model_class()
    #    try:
    #        return wanted_model.objects.get(id=wellsgeophysics.id).pk
    #    except Exception:
    #        return {}

    class Meta:
        model = WellsGeophysics
        fields = [
            "id",
            "well",
            "date",
            "organization",
            "researches",
            "conclusion",
            "doc",
        ]


class WellsLugHeightResource(resources.ModelResource):
    """
    Resource for WellsLugHeight model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsLugHeight
        fields = ["id", "lug_height", "content_type", "content_type__model", "object_id"]


class WellsChemResource(resources.ModelResource):
    """
    Resource for WellsChemResource model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsChem
        fields = ["id", "parameter", "chem_value", "content_type", "content_type__model", "object_id"]


class WellsAquiferUsageResource(resources.ModelResource):
    """
    Resource for WellsAquiferUsage model for admin import-export data
    """

    class Meta:
        model = WellsAquiferUsage
        fields = ["id", "well", "aquifer"]


class ChemCodesResource(resources.ModelResource):
    """
    Resource for ChemCodes model for admin import-export data
    """

    class Meta:
        model = ChemCodes
        fields = ("chem_id", "chem_name", "chem_formula", "chem_pdk", "chem_measure")
        import_id_fields = ("chem_id",)


class AquiferCodesResource(resources.ModelResource):
    """
    Resource for AquiferCodes model for admin import-export data
    """

    class Meta:
        model = AquiferCodes
        fields = ("aquifer_id", "aquifer_name", "aquifer_index")
        import_id_fields = ("aquifer_id",)


class DictDocOrganizationsResource(resources.ModelResource):
    """
    Resource for AquiferCodes model for admin import-export data
    """

    class Meta:
        model = DictDocOrganizations
        fields = ["id", "name"]


class WellsConditionResource(resources.ModelResource):
    """
    Resource for WellsCondition model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsCondition
        fields = ["id", "condition", "content_type", "content_type__model", "object_id"]


class WellsRateResource(resources.ModelResource):
    """
    Resource for WellsRate model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsRate
        fields = ["id", "time_measure", "rate", "content_type", "content_type__model", "object_id"]


class WellsDepthResource(resources.ModelResource):
    """
    Resource for WellsDepth model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsDepth
        fields = ["id", "depth", "content_type", "content_type__model", "object_id"]


class AttachmentsResource(resources.ModelResource):
    """
    Resource for Attachments model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = Attachments
        fields = ["id", "img", "content_type", "content_type__model", "object_id"]


class WellsWaterDepthResource(resources.ModelResource):
    """
    Resource for WellsWaterDepth model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsWaterDepth
        fields = [
            "id",
            "type_level",
            "time_measure",
            "water_depth",
            "content_type",
            "content_type__model",
            "object_id",
        ]


class WellsDrilledDataResource(resources.ModelResource):
    """
    Resource for WellsDrilledData model for admin import-export data
    """

    def before_import_row(self, row, **kwargs):
        _model = row.get("content_type__model")
        ct_model = ContentType.objects.get(model=str(_model))
        row["content_type"] = int(ct_model.id)

    class Meta:
        model = WellsDrilledData
        fields = ["id", "well", "date_start", "date_end", "drill_type", "drill_rig", "organization", "doc"]
