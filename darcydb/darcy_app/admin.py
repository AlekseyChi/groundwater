from django.contrib.gis import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .forms import (WellsForm, WellsRegimeForm, WellsWaterDepthPumpForm,
                    WellsEfwForm, DocumentsForm, BalanceForm, FieldsForm,
                    IntakesForm, WellsWaterDepthForm, WellsAquifersForm)
from .models import (Documents, Wells, Intakes, WellsRegime, WellsWaterDepth,
                     WellsRate, WellsAquifers, WellsDepression, WellsEfw,
                     WellsChem, WellsSample, DictEntities, Fields, Balance,
                     Attachments, DocumentsPath, DictPump, WellsDepth, WellsTemperature,
                     WellsConstruction, Entities, DictDocOrganizations, WellsDrilledData)
from .filters import WellsTypeFilter, TypeEfwFilter, DocTypeFilter, DocSourceFilter
from jet.admin import CompactInline
from import_export.admin import ImportExportModelAdmin
from .resources import WellsRegimeResource
import nested_admin

ADMIN_ORDERING = [
    ('darcy_app', [
        'Wells',
        'WellsEfw',
        'WellsRegime',
        'WellsSample',
        'Intakes',
        'Fields',
        'Documents',
        'DictPump',
        # 'ChemCodes',
        # 'AquiferCodes',
    ]),
]

admin.site.register(DictEntities)
admin.site.register(Entities)


class DarcyAdminArea(admin.AdminSite):
    site_header = 'Админпанель Дарси'
    site_title = 'Dарси'
    index_title = 'Админпанель Дарси'


darcy_admin = DarcyAdminArea(name='darcy_admin')


# Wells
# -------------------------------------------------------------------------------
class AttachmentsInline(nested_admin.NestedGenericTabularInline):
    model = Attachments
    fields = ('img', 'image_tag',)
    readonly_fields = ('image_tag',)
    extra = 1


class DocumentsPathInline(nested_admin.NestedTabularInline):
    model = DocumentsPath
    extra = 1


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
    model = WellsConstruction
    # classes = ('collapse',)
    extra = 1


class WellsWaterDepthDrilledInline(nested_admin.NestedGenericTabularInline):
    form = WellsWaterDepthForm
    model = WellsWaterDepth
    extra = 1
    max_num = 1


class WellsDepthInline(nested_admin.NestedGenericTabularInline):
    model = WellsDepth
    extra = 1
    max_num = 1


class WellsDrilledDataInline(nested_admin.NestedTabularInline):
    model = WellsDrilledData
    inlines = [WellsWaterDepthDrilledInline, WellsDepthInline]
    extra = 1
    max_num = 1


class WellsRateInline(nested_admin.NestedGenericTabularInline):
    model = WellsRate
    extra = 1


class WellsWaterDepthPumpInline(WellsWaterDepthDrilledInline):
    form = WellsWaterDepthPumpForm
    max_num = 1000


class WellsDepressionInline(nested_admin.NestedTabularInline):
    model = WellsDepression
    inlines = [WellsWaterDepthPumpInline, WellsRateInline]
    extra = 1
    max_num = 1


class WellsEfwInlines(nested_admin.NestedStackedInline):
    form = WellsEfwForm
    model = WellsEfw
    inlines = [WellsDepressionInline]
    max_num = 1


class WellsChemInline(nested_admin.NestedGenericTabularInline):
    model = WellsChem
    extra = 1


class WellsSampleInline(nested_admin.NestedStackedInline):
    model = WellsSample
    inlines = [WellsChemInline]
    extra = 1
    max_num = 1


class WellsAdmin(nested_admin.NestedModelAdmin):
    form = WellsForm
    model = Wells
    inlines = [DocumentsInline, WellsAquifersInline, WellsConstructionInline,
               WellsDrilledDataInline, WellsEfwInlines, WellsSampleInline, AttachmentsInline]
    fields = (
        'name', 'typo', 'head', 'moved', 'intake', 'field',
        ('latitude_degrees', 'latitude_minutes', 'latitude_seconds'),
        ('longitude_degrees', 'longitude_minutes', 'longitude_seconds'),
        'geom', 'name_gwk', 'name_drill', 'name_subject',
    )
    list_display = ("__str__", "typo",)
    list_filter = (WellsTypeFilter,)
    search_fields = ("extra", "uuid",)


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
        if getattr(request, '_editing_document', False):  # query attribute
            return False
        return super(DocumentsAdmin, self).has_delete_permission(request, obj=obj)


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
    form = WellsEfwForm
    model = WellsEfw
    inlines = [WellsDepressionInline]
    list_display = ("well", "date", "type_efw")
    list_filter = ('date', 'well', TypeEfwFilter)


darcy_admin.register(WellsEfw, WellsEfwAdmin)


# WellsRegime
# -------------------------------------------------------------------------------
class WellsWaterDepthInline(WellsWaterDepthDrilledInline):
    max_num = 1000


class WellsTemperatureInline(nested_admin.NestedGenericTabularInline):
    model = WellsTemperature
    extra = 1


class WellsRegimeAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    form = WellsRegimeForm
    model = WellsRegime
    inlines = [WellsWaterDepthInline, WellsTemperatureInline, WellsRateInline]
    list_display = ("well", "date")
    list_filter = ('well', ('date', DateFieldListFilter),)
    resource_class = WellsRegimeResource


darcy_admin.register(WellsRegime, WellsRegimeAdmin)


# WellsSample
# -------------------------------------------------------------------------------
class WellsSampleAdmin(nested_admin.NestedModelAdmin):
    model = WellsSample
    inlines = [WellsChemInline]
    list_display = ("well", "date", "name")
    search_fields = ("name",)
    list_filter = ('date', 'well')


darcy_admin.register(WellsSample, WellsSampleAdmin)


# Others
# -------------------------------------------------------------------------------
darcy_admin.register(DictPump)
darcy_admin.register(DictDocOrganizations)
