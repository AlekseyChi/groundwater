import datetime

import nested_admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.gis import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
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
from .models import (
    AquiferCodes,
    Attachments,
    Balance,
    DictDocOrganizations,
    DictEntities,
    DictEquipment,
    Documents,
    DocumentsPath,
    Entities,
    Fields,
    Intakes,
    License,
    LicenseToWells,
    WaterUsers,
    WaterUsersChange,
    Wells,
    WellsAquifers,
    WellsChem,
    WellsConstruction,
    WellsDepression,
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
from .resources import WellsRegimeResource
from .utils.passport_gen import generate_passport
from .utils.pump_journals_gen import generate_pump_journal

admin.site.register(DictEntities)
admin.site.register(Entities)


class DarcyAdminArea(admin.AdminSite):
    site_header = "Админпанель Дарси"
    site_title = "Dарси"
    index_title = "Админпанель Дарси"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("create_doc_auto/<int:intake>/", self.admin_view(self.create_doc_auto))]
        return my_urls + urls

    def create_doc_auto(self, request, intake):
        code = DictEntities.objects.get(entity__name="тип документа", name="Журнал опытно-фильтрационных работ")
        wells = WellsAquifers.objects.all().values("well")
        efws = WellsEfw.objects.filter(
            well__intake__id=intake, type_efw__name="откачки одиночные опытные", well__in=wells
        )
        print(efws)
        for qs in efws:
            doc_instance = qs.doc
            if not doc_instance:
                doc_instance = Documents.objects.create(
                    name=f"Журнал опытной откачки из скважины №{qs.well.name} от {qs.date}",
                    typo=code,
                    creation_date=datetime.datetime.now().date(),
                    object_id=qs.pk,
                )
                qs.doc = doc_instance
                qs.save()
            rest_efw = WellsEfw.objects.filter(
                well=qs.well,
                type_efw__name="восстановление уровня",
                date__lte=qs.date + datetime.timedelta(days=4),
                date__gte=qs.date - datetime.timedelta(days=4),
            ).first()
            if rest_efw:
                rest_efw.doc = doc_instance
                rest_efw.save()
            generate_pump_journal(qs, doc_instance)

        code = DictEntities.objects.get(entity__name="тип документа", name="Паспорт скважины")
        pswds = Wells.objects.filter(intake__id=intake, id__in=wells)
        for qs in pswds:
            doc_instance = qs.docs.filter(typo=code).first()
            if not doc_instance:
                doc_instance = qs.docs.create(
                    name=f"Паспорт скважины №{qs.name}({qs.pk})",
                    typo=code,
                    creation_date=datetime.datetime.now().date(),
                    object_id=qs.pk,
                )
            generate_passport(qs, doc_instance)
        return HttpResponseRedirect(reverse("admin:index"))


darcy_admin = DarcyAdminArea(name="darcy_admin")


# Wells
# -------------------------------------------------------------------------------
class AttachmentsInline(nested_admin.NestedGenericTabularInline):
    model = Attachments
    fields = (
        "img",
        "image_tag",
    )
    readonly_fields = ("image_tag",)
    extra = 1


class DocumentsPathInline(nested_admin.NestedTabularInline):
    model = DocumentsPath
    extra = 1

    def presigned_url(self, instance):
        return instance.presigned_url


class DocumentsInline(nested_admin.NestedGenericStackedInline):
    form = DocumentsForm
    model = Documents
    inlines = [DocumentsPathInline]
    extra = 1


class WellsAquifersInline(nested_admin.NestedTabularInline):
    model = WellsAquifers
    form = WellsAquifersForm
    extra = 1


class WellsConstructionInline(nested_admin.NestedTabularInline):
    form = WellsConstructionForm
    model = WellsConstruction
    # classes = ("collapse",)
    extra = 1


class WellsWaterDepthPumpInline(nested_admin.NestedGenericTabularInline):
    model = WellsWaterDepth
    form = WellsWaterDepthPumpForm
    extra = 1
    max_num = 1000
    # min_num = 1


class WellsWaterDepthDrilledInline(WellsWaterDepthPumpInline):
    form = WellsWaterDepthForm
    max_num = 1


class WellsDepthInline(nested_admin.NestedGenericTabularInline):
    model = WellsDepth
    extra = 1
    max_num = 1


class WellsLugHeightInline(nested_admin.NestedGenericTabularInline):
    model = WellsLugHeight
    extra = 1
    max_num = 1


class WellsDrilledDataInline(nested_admin.NestedTabularInline):
    model = WellsDrilledData
    inlines = [WellsWaterDepthDrilledInline, WellsDepthInline]
    extra = 1
    max_num = 1


class WellsRatePumpInline(nested_admin.NestedGenericTabularInline):
    model = WellsRate
    extra = 1


class WellsRateInline(WellsRatePumpInline):
    model = WellsRate
    form = WellsRateForm
    extra = 1


class WellsDepressionInline(nested_admin.NestedTabularInline):
    model = WellsDepression
    form = WellsDepressionForm
    inlines = [WellsWaterDepthPumpInline, WellsRatePumpInline]
    extra = 1
    max_num = 1


class WellsEfwInlines(nested_admin.NestedStackedInline):
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
    model = WellsChem
    extra = 1


class WellsSampleInline(nested_admin.NestedStackedInline):
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


class WellsGeophysicsInline(nested_admin.NestedStackedInline):
    model = WellsGeophysics
    inlines = [WellsDepthInline, WellsWaterDepthDrilledInline, AttachmentsInline]
    extra = 1
    max_num = 1


class WellsLithologyInline(nested_admin.NestedTabularInline):
    model = WellsLithology
    form = WellsLithologyForm
    extra = 1


class LicenseToWellsInline(nested_admin.NestedTabularInline):
    model = LicenseToWells
    extra = 1


class WellsAdmin(nested_admin.NestedModelAdmin):
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


darcy_admin.register(Wells, WellsAdmin)


# Documents
# -------------------------------------------------------------------------------
class DocumentsAdmin(nested_admin.NestedModelAdmin):
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


darcy_admin.register(Documents, DocumentsAdmin)


# Intakes
# -------------------------------------------------------------------------------
class WellsInline(CompactInline):
    form = WellsForm
    model = Wells
    show_change_link = True
    extra = 1


class IntakesAdmin(admin.ModelAdmin):
    form = IntakesForm
    model = Intakes
    inlines = [WellsInline]
    list_display = ("intake_name",)
    search_fields = ("intake_name",)


darcy_admin.register(Intakes, IntakesAdmin)


# Fields
# -------------------------------------------------------------------------------
class BalanceInline(nested_admin.NestedGenericTabularInline):
    model = Balance
    form = BalanceForm
    extra = 1


class FieldsAdmin(nested_admin.NestedModelAdmin):
    form = FieldsForm
    model = Fields
    inlines = [DocumentsInline, BalanceInline]
    list_display = ("field_name",)
    search_fields = ("field_name",)


darcy_admin.register(Fields, FieldsAdmin)


# WellsEfw
# -------------------------------------------------------------------------------
class WellsEfwAdmin(nested_admin.NestedModelAdmin):
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


darcy_admin.register(WellsEfw, WellsEfwAdmin)


# WellsRegime
# -------------------------------------------------------------------------------
class WellsWaterDepthInline(WellsWaterDepthDrilledInline):
    max_num = 1000


class WellsTemperatureInline(nested_admin.NestedGenericTabularInline):
    model = WellsTemperature
    form = WellsTemperatureForm
    extra = 1


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


darcy_admin.register(WellsRegime, WellsRegimeAdmin)


# WellsSample
# -------------------------------------------------------------------------------
class WellsSampleAdmin(nested_admin.NestedModelAdmin):
    model = WellsSample
    inlines = [WellsChemInline]
    list_display = ("well", "date", "name")
    search_fields = ("name",)
    list_filter = ("date", "well")


darcy_admin.register(WellsSample, WellsSampleAdmin)


# WaterUsers
# -------------------------------------------------------------------------------


class WaterUsersChangeInline(nested_admin.NestedTabularInline):
    model = WaterUsersChange
    extra = 1


class WaterUsersAdmin(nested_admin.NestedModelAdmin):
    model = WaterUsers
    inlines = [WaterUsersChangeInline]
    list_display = search_fields = list_filter = ("name",)


darcy_admin.register(WaterUsers, WaterUsersAdmin)


# License
# -------------------------------------------------------------------------------


class LicenseAdmin(nested_admin.NestedModelAdmin):
    model = License
    inlines = [LicenseToWellsInline, WaterUsersChangeInline]
    list_display = ("name",)
    search_fields = ("name", "date_start", "date_end", "department")
    list_filter = ("name", "date_start", "date_end")


darcy_admin.register(License, LicenseAdmin)


# Others
# -------------------------------------------------------------------------------


class DictEquipmentAdmin(nested_admin.NestedModelAdmin):
    model = DictEquipment
    form = DictEquipmentForm


darcy_admin.register(DictEquipment, DictEquipmentAdmin)
darcy_admin.register(DictDocOrganizations)
darcy_admin.register(AquiferCodes)
# darcy_admin.register(DocumentsCreatorAdmin)
