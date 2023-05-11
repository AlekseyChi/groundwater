from django.contrib.gis import admin
from django.apps import apps
from django.contrib.gis import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .forms import (WellsForm, WellsRegimeForm, WellsDepressionForm,
                    WellsEfwForm, DocumentsForm, BalanceForm, FieldsForm,
                    IntakesForm)
from .models import (Documents, Wells, Intakes, WellsRegime, WellsWaterDepth, 
                     WellsRate, WellsAquifers, WellsDepression, WellsEfw,
                     WellsChem, WellsSample, DictEntities, Fields, Balance,
                     Attachments, DocumentsPath, DictPump, WellsAquiferUsage,)

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
    ]),
]


class DarcyAdminArea(admin.AdminSite):
    site_header =  'Админпанель Дарси'
    site_title = 'Dарси'
    index_title = 'Админпанель Дарси'

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        for app_name, object_list in ADMIN_ORDERING:
            app = app_dict[app_name]
            app['models'].sort(key=lambda x: object_list.index(x['object_name']))
            yield app


darcy_admin = DarcyAdminArea(name='darcy_admin')


class BalanceInline(GenericTabularInline):
    model = Balance
    form = BalanceForm
    classes = ('collapse',)
    extra = 1


class WellsInline(admin.StackedInline):
    # fields = (('name', 'typo'), ('head', 'aquifer'), 'geom')
    form = WellsForm
    classes = ('collapse',)
    model = Wells
    extra = 1


class WellsAquifersUsageInline(admin.TabularInline):
    model = WellsAquiferUsage
    extra = 1


class WellsWaterDepthInline(GenericTabularInline):
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
    classes = ('collapse',)
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

class WellsRegimeAdmin(admin.ModelAdmin):
    form = WellsRegimeForm
    model = WellsRegime
    inlines = [WellsWaterDepthInline, WellsRateInline]
    fields = (('well', 'date',),)
    list_display = ("well", "date")


darcy_admin.register(WellsRegime, WellsRegimeAdmin)


class DocumentsAdmin(admin.ModelAdmin):
    form = DocumentsForm
    model = Documents
    inlines = [DocumentsPathInline]
    list_display = ("typo", "name", "creation_date", "source")


darcy_admin.register(Documents, DocumentsAdmin)


class IntakesAdmin(admin.ModelAdmin):
    form = IntakesForm
    model = Intakes
    inlines = [WellsInline]


darcy_admin.register(Intakes, IntakesAdmin)


class WellsAdmin(admin.ModelAdmin):
    form = WellsForm
    model = Wells
    inlines = [WellsAquifersUsageInline, DocumentsInline, WellsAquifersInline, AttachmentsInline]
    list_display = ("name", "typo",)


darcy_admin.register(Wells, WellsAdmin)


class WellsEfwAdmin(admin.ModelAdmin):
    form = WellsEfwForm
    model = WellsEfw
    inlines = [WellsDepressionInline]
    list_display = ("well", "date", "type_efw")


darcy_admin.register(WellsEfw, WellsEfwAdmin)


class WellsSampleAdmin(admin.ModelAdmin):
    model = WellsSample
    inlines = [WellsChemInline]
    list_display = ("well", "date", "name")


darcy_admin.register(WellsSample, WellsSampleAdmin)


class FieldsAdmin(admin.ModelAdmin):
    form = FieldsForm
    model = Fields
    inlines = [DocumentsInline, BalanceInline]


darcy_admin.register(Fields, FieldsAdmin)
darcy_admin.register(DictPump)
