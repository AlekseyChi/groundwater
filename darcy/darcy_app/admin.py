from django.contrib.gis import admin
from django.apps import apps
from django.contrib.gis import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .forms import WellsForm
from .models import (Documents, Wells, Intakes, WellsRegime, WellsWaterDepth, 
                     WellsRate, WellsAquifers, WellsDepression, WellsEfw,
                     WellsChem, WellsSample, DictEntities, Fields, Balance,
                     Attachments, DocumentsPath)

ADMIN_ORDERING = [
    ('darcy_app', [
        'Wells',
        'WellsEfw',
        'WellsRegime',
        'WellsSample',
        'Intakes',
        'Fields',
        'Documents',
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


class IntakesForm(forms.ModelForm):
    class Meta:
        model = Intakes
        fields = '__all__'
        widgets = {
                'geom': forms.OSMWidget(
                    attrs={
                        "display_raw": True,
                        "default_lat": 54.5,
                        "default_lon": 36.28,
                        },
                    )
                }

    def __init__(self, *args, **kwargs):
        super(IntakesForm, self).__init__(*args, **kwargs)


class FieldsForm(forms.ModelForm):
    class Meta:
        model = Fields
        fields = '__all__'
        widgets = {
                'geom': forms.OSMWidget(
                    attrs={
                        "display_raw": True,
                        "default_lat": 54.5,
                        "default_lon": 36.28,
                        },
                    )
                }

    def __init__(self, *args, **kwargs):
        super(FieldsForm, self).__init__(*args, **kwargs)


class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Documents
        # fields = '__all__'
        exclude = ('content_type', 'object_id', 'content_object')

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        self.fields['typo'].queryset = DictEntities.objects.filter(entity=2)
        self.fields['source'].queryset = DictEntities.objects.filter(entity=5)
        self.fields['org_executor'].queryset = DictEntities.objects.filter(entity=5)
        self.fields['org_customer'].queryset = DictEntities.objects.filter(entity=5)


class WellsRegimeForm(forms.ModelForm):
    class Meta:
        model = WellsRegime
        exclude = ('doc',)
        
    def __init__(self, *args, **kwargs):
        super(WellsRegimeForm, self).__init__(*args, **kwargs)


class WellsEfwForm(forms.ModelForm):
    class Meta:
        model = WellsEfw
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WellsEfwForm, self).__init__(*args, **kwargs)
        self.fields['type_efw'].queryset = DictEntities.objects.filter(entity=3)
        self.fields['pump_type'].queryset = DictEntities.objects.filter(entity=4)


class WellsDepressionForm(forms.ModelForm):
    water_depth = forms.FloatField(label='Глубина воды, м', required=True) 
    class Meta:
        model = WellsDepression
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WellsDepressionForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            self.fields['water_depth'].initial = kwargs['instance'].waterdepths.first().water_depth

    def save(self, *args, **kwargs):
        water_depth = self.cleaned_data.pop('water_depth')
        instance = super(WellsDepressionForm, self).save(*args, **kwargs)
        if water_depth:
            if self.instance.waterdepths.first():
                watinstance = self.instance.waterdepths.first()
                watinstance.water_depth = water_depth
                watinstance.save()
            else:
                self.instance.waterdepths.create(object_id=self.instance.pk, water_depth=water_depth)
        return instance


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BalanceForm, self).__init__(*args, **kwargs)
        self.fields['typo'].queryset = DictEntities.objects.filter(entity=6)


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
    # fields = (
    #         'typo',
    #         ('name', 'creation_date'),
    #         ('source', 'org_executor', 'org_customer'),
    #         )
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
    inlines = [DocumentsInline, WellsAquifersInline, AttachmentsInline]
    list_display = ("name", "typo", "aquifer")


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
