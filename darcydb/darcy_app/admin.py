import datetime

import nested_admin
from django.contrib.admin import DateFieldListFilter, register
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis import admin
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from jet.admin import CompactInline

from .filters import DocSourceFilter, DocTypeFilter, TypeEfwFilter, WellsTypeFilter
from .forms import (
    BalanceForm,
    DictEquipmentForm,
    DocumentsForm,
    FieldsForm,
    IntakesForm,
    WellsAquifersForm,
    WellsConstructionForm,
    WellsDepressionForm,
    WellsEfwForm,
    WellsForm,
    WellsLithologyForm,
    WellsRateForm,
    WellsRegimeForm,
    WellsTemperatureForm,
    WellsWaterDepthForm,
    WellsWaterDepthPumpForm,
)
from .models import *
from .resources import *
from .utils.passport_gen import generate_passport
from .utils.pump_journals_gen import generate_pump_journal


class DarcyAdminArea(admin.AdminSite):
    site_header = "Админпанель Дарси"
    site_title = "Dарси"
    index_title = "Админпанель Дарси"


darcy_admin = DarcyAdminArea(name="darcy_admin")


@register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_filter = ("model", "app_label")
    list_display = ("id", "app_label", "model")

    # Remove the delete Admin Action for this Model
    actions = None

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass


# Wells
# -------------------------------------------------------------------------------


class AttachmentsInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for Attachments  model
    """

    model = Attachments
    fields = (
        "img",
        "image_tag",
    )
    readonly_fields = ("image_tag",)
    extra = 1


class DocumentsPathInline(nested_admin.NestedTabularInline):
    """
    Inline tab for DocumentsPath  model
    """

    model = DocumentsPath
    extra = 1

    def presigned_url(self, instance):
        return instance.presigned_url


class DocumentsInline(nested_admin.NestedGenericStackedInline):
    """
    Inline tab for DocumentsForm  model
    """

    form = DocumentsForm
    model = Documents
    inlines = [DocumentsPathInline]
    extra = 1


class WellsAquifersInline(nested_admin.NestedTabularInline):
    """
    Inline tab for WellsAquifers  model
    """

    model = WellsAquifers
    form = WellsAquifersForm
    extra = 1


class WellsConstructionInline(nested_admin.NestedTabularInline):
    """
    Inline tab for WellsConstruction  model
    """

    form = WellsConstructionForm
    model = WellsConstruction
    # classes = ("collapse",)
    extra = 1


class WellsWaterDepthPumpInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for WellsWaterDepth  model
    """

    model = WellsWaterDepth
    form = WellsWaterDepthPumpForm
    extra = 1
    max_num = 1000
    # min_num = 1


class WellsWaterDepthDrilledInline(WellsWaterDepthPumpInline):
    """
    Inline tab for WellsWaterDepth  model
    """

    form = WellsWaterDepthForm
    max_num = 1


class WellsDepthInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for WellsDepth  model
    """

    form = WellsWaterDepthForm
    max_num = 1
    model = WellsDepth
    extra = 1
    max_num = 1


class WellsLugHeightInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for WellsLugHeight  model
    """

    model = WellsLugHeight
    extra = 1
    max_num = 1


@register(WellsLugHeight)
class WellsLugHeightAdmin(ImportExportModelAdmin):
    resource_class = WellsLugHeightResource


class WellsDrilledDataInline(nested_admin.NestedTabularInline):
    """
    Inline tab for WellsDrilledData  model
    """

    model = WellsDrilledData
    inlines = [WellsWaterDepthDrilledInline, WellsDepthInline]
    extra = 1
    max_num = 1


class WellsRatePumpInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for WellsRate  model
    """

    model = WellsRate
    extra = 1


class WellsRateInline(WellsRatePumpInline):
    model = WellsRate
    form = WellsRateForm
    extra = 1


class WellsDepressionInline(nested_admin.NestedTabularInline):
    """
    Inline tab for WellsDepression  model
    """    
    model = WellsDepression
    form = WellsDepressionForm
    inlines = [WellsWaterDepthPumpInline, WellsRatePumpInline]
    extra = 1
    max_num = 1


class WellsEfwInlines(nested_admin.NestedStackedInline):
    """
    Inline tab for WellsEfw  model
    """

    form = WellsEfwForm
    model = WellsEfw
    inlines = [WellsLugHeightInline, WellsWaterDepthDrilledInline, WellsDepressionInline]
    extra = 1

    def get_extra(self, request, obj=None, **kwargs):
        count = self.model.objects.filter(well=obj).count()
        if count >= 1:
            return 0
        return self.extra


class WellsChemInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for WellsChem  model
    """

    model = WellsChem
    extra = 1


@register(WellsChem)
class WellsChemResourceAdmin(ImportExportModelAdmin):
    resource_class = WellsChemResource


class WellsSampleInline(nested_admin.NestedStackedInline):
    """
    Inline tab for WellsSample  model
    """

    model = WellsSample
    inlines = [WellsChemInline, AttachmentsInline]
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(doc__isnull=False)

    def get_extra(self, request, obj=None, **kwargs):
        count = self.model.objects.filter(well=obj, doc__isnull=False).count()
        if count >= 1:
            return 0
        return self.extra


@register(WellsGeophysics)
class WellsGeophysicsAdmin(ImportExportModelAdmin):
    resource_class = WellsGeophysicsResource


class WellsGeophysicsInline(nested_admin.NestedStackedInline):
    """
    Inline tab for WellsGeophysics  model
    """

    model = WellsGeophysics
    inlines = [WellsDepthInline, WellsWaterDepthDrilledInline, AttachmentsInline]
    extra = 1
    max_num = 1


@register(WellsLithology)
class WellsLithologyAdmin(ImportExportModelAdmin):
    resource_class = WellsLithologyResource


class WellsLithologyInline(nested_admin.NestedTabularInline):
    """
    Inline tab for WellsLithology  model
    """

    model = WellsLithology
    form = WellsLithologyForm
    extra = 1


class LicenseToWellsInline(nested_admin.NestedTabularInline):
    """
    Inline tab for LicenseToWells  model
    """

    model = LicenseToWells
    extra = 1


@register(Wells)
class WellsAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = WellResource
    change_form_template = "darcy_app/doc_change_form.html"
    form = WellsForm
    model = Wells
    inlines = [
        LicenseToWellsInline,
        WellsAquifersInline,
        WellsLithologyInline,
        WellsConstructionInline,
        WellsDrilledDataInline,
        WellsEfwInlines,
        WellsGeophysicsInline,
        WellsSampleInline,
        DocumentsInline,
        AttachmentsInline,
    ]
    fields = (
        "name",
        "typo",
        "head",
        "moved",
        "intake",
        "field",
        ("latitude_degrees", "latitude_minutes", "latitude_seconds"),
        ("longitude_degrees", "longitude_minutes", "longitude_seconds"),
        "geom",
        "name_gwk",
        "name_drill",
        "name_subject",
        "comments",
    )
    list_display = (
        "__str__",
        "typo",
    )
    list_filter = (WellsTypeFilter,)
    search_fields = (
        "extra",
        "uuid",
    )

    list_select_related = ("typo", "moved", "intake", "field")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("typo", "typo__entity", "moved", "moved__entity", "intake", "field").prefetch_related(
            "docs",
            "docs__typo",
            "docs__source",
            "docs__org_executor",
            "docs__org_customer",
            "docs__links",
            "attachments",
            "field__docs",
            "field__docs__typo",
            "field__docs__source",
            "field__docs__org_executor",
            "field__docs__org_customer",
            "field__docs__links",
            "field__balances",
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if "_generate_doc" in request.POST:
            code = DictEntities.objects.get(entity__name="тип документа", name="Паспорт скважины")
            doc_instance = form.instance.docs.filter(typo=code).last()
            if not doc_instance:
                doc_instance = form.instance.docs.create(
                    name=f"Паспорт скважины №{form.instance.pk}",
                    typo=code,
                    creation_date=datetime.datetime.now().date(),
                    object_id=form.instance.pk,
                )
            generate_passport(form.instance, doc_instance)
            doc_file = DocumentsPath.objects.filter(doc=doc_instance).last()
            self.message_user(request, mark_safe(f'Паспорт создан. <a href="{doc_file.path.url}">Скачать паспорт</a>'))

    def response_change(self, request, obj):
        if "_generate_doc" in request.POST:
            return HttpResponseRedirect(request.path)
        return super().response_change(request, obj)


# Documents
# -------------------------------------------------------------------------------
@register(Documents)
class DocumentsAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = DocumentsResource
    form = DocumentsForm
    model = Documents
    inlines = [DocumentsPathInline]
    list_display = ("typo", "name", "creation_date", "source")
    list_filter = (DocTypeFilter, "creation_date", DocSourceFilter)
    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        if getattr(request, "_editing_document", False):  # query attribute
            return False
        return super().has_delete_permission(request, obj=obj)


# Intakes
# -------------------------------------------------------------------------------
class WellsInline(CompactInline):
    form = WellsForm
    model = Wells
    show_change_link = True
    extra = 1


@register(Intakes)
class IntakesAdmin(ImportExportModelAdmin):
    resource_class = IntakesResource
    form = IntakesForm
    model = Intakes
    inlines = [WellsInline]
    list_display = ("intake_name",)
    search_fields = ("intake_name",)


# Fields
# -------------------------------------------------------------------------------
class BalanceInline(nested_admin.NestedGenericTabularInline):
    model = Balance
    form = BalanceForm
    extra = 1


@register(Balance)
class BalanceAdmin(ImportExportModelAdmin):
    resource_class = BalanceResource


@register(Fields)
class FieldsAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = FieldsResource
    form = FieldsForm
    model = Fields
    inlines = [DocumentsInline, BalanceInline]
    list_display = ("field_name",)
    search_fields = ("field_name",)


# WellsEfw
# -------------------------------------------------------------------------------
@register(WellsEfw)
class WellsEfwAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = WellsEfwResource
    change_form_template = "darcy_app/doc_change_form.html"
    form = WellsEfwForm
    model = WellsEfw
    inlines = [WellsLugHeightInline, WellsWaterDepthDrilledInline, WellsDepressionInline]
    list_display = ("well", "date", "type_efw")
    list_filter = ("date", "well", TypeEfwFilter)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if "_generate_doc" in request.POST:
            code = DictEntities.objects.get(entity__name="тип документа", name="Журнал опытно-фильтрационных работ")
            doc_instance = form.instance.doc
            if not doc_instance:
                doc_instance = Documents.objects.create(
                    name=f"Журнал опытной откачки из скважины №{form.instance.well} от {form.instance.date}",
                    typo=code,
                    creation_date=datetime.datetime.now().date(),
                    object_id=form.instance.pk,
                )
                form.instance.doc = doc_instance
                form.instance.save()
            generate_pump_journal(form.instance, doc_instance)
            doc_file = DocumentsPath.objects.filter(doc=doc_instance).last()
            self.message_user(request, mark_safe(f'Журнал создан.<a href="{doc_file.path.url}">Скачать журнал</a>'))

    def response_change(self, request, obj):
        if "_generate_doc" in request.POST:
            return HttpResponseRedirect(request.path)
        return super().response_change(request, obj)


# WellsRegime
# -------------------------------------------------------------------------------
class WellsWaterDepthInline(WellsWaterDepthDrilledInline):
    """
    Inline tab for WellsTemperature model
    """

    max_num = 1000


@register(WellsTemperature)
class WellsTemperatureAdmin(ImportExportModelAdmin):
    resource_class = WellsTemperatureResource


class WellsTemperatureInline(nested_admin.NestedGenericTabularInline):
    """
    Inline tab for WellsTemperature model
    """

    model = WellsTemperature
    form = WellsTemperatureForm
    extra = 1


@register(WellsRegime)
class WellsRegimeAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    form = WellsRegimeForm
    model = WellsRegime
    inlines = [WellsWaterDepthInline, WellsTemperatureInline, WellsRateInline]
    list_display = ("well", "date")
    list_filter = (
        "well",
        ("date", DateFieldListFilter),
    )
    resource_class = WellsRegimeResource


# WellsSample
# -------------------------------------------------------------------------------
@register(WellsSample)
class WellsSampleAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = WellsSampleResource
    model = WellsSample
    inlines = [WellsChemInline]
    list_display = ("well", "date", "name")
    search_fields = ("name",)
    list_filter = ("date", "well")


# WaterUsers
# -------------------------------------------------------------------------------


@register(WaterUsersChange)
class WaterUsersChangeAdmin(ImportExportModelAdmin):
    resource_class = WaterUsersChangeResource


class WaterUsersChangeInline(nested_admin.NestedTabularInline):
    """
    Inline tab for WaterUsersChange model
    """

    model = WaterUsersChange
    extra = 1


@register(WaterUsers)
class WaterUsersAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = WaterUsersResouce
    model = WaterUsers
    inlines = [WaterUsersChangeInline]
    list_display = search_fields = list_filter = ("name",)


# License
# -------------------------------------------------------------------------------


@register(License)
class LicenseAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = LicenseResource
    model = License
    inlines = [LicenseToWellsInline, WaterUsersChangeInline]
    list_display = ("name", "date_start", "date_end",)
    search_fields = ("name", "date_start", "date_end", "department")
    list_filter = ("name", "date_start", "date_end")


@register(LicenseToWells)
class LicenseToWellsAdmin(ImportExportModelAdmin):
    resource_class = LicenseToWellsResource
    list_display = ("id", "well", "license")


# Others
# -------------------------------------------------------------------------------


@register(DictEquipment)
class DictEquipmentAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    resource_class = DictEquipmentResource
    model = DictEquipment
    form = DictEquipmentForm


@register(DictEntities)
class DictEntitiesAdmin(ImportExportModelAdmin):
    resource_class = DictEntitiesResource
    search_fields = (
        "name",
        "entity__name",
    )
    list_display = ("id", "name", "entity")


@register(Entities)
class EntitiesAdmin(ImportExportModelAdmin):
    resource_class = EntitiesResource
    search_fields = ("name",)
    list_display = ("id", "name")


@register(AquiferCodes)
class AquiferCodesAdmin(ImportExportModelAdmin):
    resource_class = AquiferCodesResource
    list_display = ("aquifer_id", "aquifer_name", "aquifer_index")


@register(ChemCodes)
class ChemCodesAdmin(ImportExportModelAdmin):
    resource_class = ChemCodesResource
    list_display = ("chem_id", "chem_name", "chem_formula", "chem_pdk", "chem_measure")


@register(WellsAquiferUsage)
class WellsAquiferUsageAdmin(ImportExportModelAdmin):
    resource_class = WellsAquiferUsageResource
    list_display = ("id", "well", "aquifer")


darcy_admin.register(Wells, WellsAdmin)
darcy_admin.register(Documents, DocumentsAdmin)
darcy_admin.register(Intakes, IntakesAdmin)
darcy_admin.register(Fields, FieldsAdmin)
darcy_admin.register(WellsEfw, WellsEfwAdmin)
darcy_admin.register(WellsRegime, WellsRegimeAdmin)
darcy_admin.register(WellsSample, WellsSampleAdmin)
darcy_admin.register(WaterUsers, WaterUsersAdmin)
darcy_admin.register(License, LicenseAdmin)
darcy_admin.register(DictEquipment, DictEquipmentAdmin)
darcy_admin.register(DictDocOrganizations)
darcy_admin.register(AquiferCodes)
