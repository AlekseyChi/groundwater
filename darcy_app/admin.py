from django.contrib.gis import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .forms import (WellsForm, WellsRegimeForm, WellsDepressionForm,
                    WellsEfwForm, DocumentsForm, BalanceForm, FieldsForm,
                    IntakesForm, WellsWaterDepthForm)
from .models import (Documents, Wells, Intakes, WellsRegime, WellsWaterDepth, 
                     WellsRate, WellsAquifers, WellsDepression, WellsEfw,
                     WellsChem, WellsSample, DictEntities, Fields, Balance,
                     Attachments, DocumentsPath, DictPump, WellsAquiferUsage,
                     WellsConstruction, Entities)
from .filters import WellsTypeFilter, TypeEfwFilter, DocTypeFilter, DocSourceFilter
from jet.admin import CompactInline
from import_export.admin import ImportExportModelAdmin
from .resources import WellsRegimeResource

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
    site_header =  'Админпанель Дарси'
    site_title = 'Dарси'
    index_title = 'Админпанель Дарси'


darcy_admin = DarcyAdminArea(name='darcy_admin')


class BalanceInline(GenericTabularInline):
    model = Balance
    form = BalanceForm
    # classes = ('collapse',)
    extra = 1


class WellsInline(CompactInline):
    form = WellsForm
    model = Wells
    show_change_link = True
    extra = 1


class WellsAquifersUsageInline(admin.TabularInline):
    model = WellsAquiferUsage
    extra = 1


class WellsWaterDepthInline(GenericTabularInline):
    form = WellsWaterDepthForm
    model = WellsWaterDepth
    extra = 1


class WellsRateInline(GenericTabularInline):
    model = WellsRate
    extra = 1


class WellsDepressionInline(admin.TabularInline):
    form = WellsDepressionForm
    model = WellsDepression
    extra = 1


class WellsChemInline(GenericTabularInline):
    model = WellsChem
    extra = 1


class WellsAquifersInline(admin.TabularInline):
    model = WellsAquifers
    # classes = ('collapse',)
    extra = 1


class WellsConstructionInline(admin.TabularInline):
    model = WellsConstruction
    # classes = ('collapse',)
    extra = 1


class DocumentsInline(GenericStackedInline):
    form = DocumentsForm
    model = Documents
    classes = ('collapse',)
    extra = 1
            

class AttachmentsInline(GenericTabularInline):
    model = Attachments
    fields = ( 'img', 'image_tag', )
    readonly_fields = ('image_tag',)
    extra = 1


class DocumentsPathInline(admin.TabularInline):
    model = DocumentsPath
    extra = 1


class WellsRegimeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    form = WellsRegimeForm
    model = WellsRegime
    inlines = [WellsWaterDepthInline, WellsRateInline]
    list_display = ("well", "date")
    list_filter = ('well', ('date', DateFieldListFilter),)
    resource_class = WellsRegimeResource


darcy_admin.register(WellsRegime, WellsRegimeAdmin)


class DocumentsAdmin(admin.ModelAdmin):
    form = DocumentsForm
    model = Documents
    inlines = [DocumentsPathInline]
    list_display = ("typo", "name", "creation_date", "source")
    list_filter = (DocTypeFilter, "creation_date", DocSourceFilter)
    search_fields = ("name", )


darcy_admin.register(Documents, DocumentsAdmin)


class IntakesAdmin(admin.ModelAdmin):
    form = IntakesForm
    model = Intakes
    inlines = [WellsInline]
    list_display = ("intake_name",)
    search_fields = ("intake_name", )


darcy_admin.register(Intakes, IntakesAdmin)


class WellsAdmin(admin.ModelAdmin):
    form = WellsForm
    model = Wells
    inlines = [WellsAquifersUsageInline, DocumentsInline, WellsAquifersInline, WellsConstructionInline, AttachmentsInline]
    fields = (
            'name', 'typo', 'head', 'moved', 'intake', 'field',
            ('latitude_degrees', 'latitude_minutes', 'latitude_seconds'),
            ('longitude_degrees', 'longitude_minutes', 'longitude_seconds'),
            'geom', 'name_gwk', 'name_drill', 'name_subject',
            )
    list_display = ("__str__", "typo",)
    list_filter = (WellsTypeFilter,)
    search_fields = ("extra", "uuid", )


darcy_admin.register(Wells, WellsAdmin)


class WellsEfwAdmin(admin.ModelAdmin):
    form = WellsEfwForm
    model = WellsEfw
    inlines = [WellsDepressionInline]
    list_display = ("well", "date", "type_efw")
    list_filter = ('date', 'well', TypeEfwFilter)


darcy_admin.register(WellsEfw, WellsEfwAdmin)


class WellsSampleAdmin(admin.ModelAdmin):
    model = WellsSample
    inlines = [WellsChemInline]
    list_display = ("well", "date", "name")
    search_fields = ("name", )
    list_filter = ('date', 'well')


darcy_admin.register(WellsSample, WellsSampleAdmin)


class FieldsAdmin(admin.ModelAdmin):
    form = FieldsForm
    model = Fields
    inlines = [DocumentsInline, BalanceInline]
    list_display = ("field_name",)
    search_fields = ("field_name",)


darcy_admin.register(Fields, FieldsAdmin)
darcy_admin.register(DictPump)
# darcy_admin.register(AquiferCodes)
# darcy_admin.register(ChemCodes)


