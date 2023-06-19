from django.contrib.gis import forms
from django.utils import timezone
from django.contrib.admin.widgets import AdminTextInputWidget
from django.contrib.postgres.forms import SimpleArrayField
from .models import (Wells, DictEntities, Intakes, Fields, Documents, Balance,
                     WellsRegime, WellsDepression, WellsEfw, WellsConstruction,
                     WellsWaterDepth)
from django.contrib.gis.geos import Point


class GeoWidget(forms.OSMWidget):
    template_name = 'gis/custom_layers.html'


class WellsForm(forms.ModelForm):
    latitude_degrees = forms.IntegerField(min_value=-90, max_value=90, required=True, label='CШ (град.)')
    latitude_minutes = forms.IntegerField(min_value=0, max_value=60, required=True, label='CШ (мин.)')
    latitude_seconds = forms.DecimalField(min_value=0, max_value=60, required=True, label='CШ (сек.)')
    longitude_degrees = forms.IntegerField(min_value=-180, max_value=180, required=True, label='ВД (град.)')
    longitude_minutes = forms.IntegerField(min_value=0, max_value=60, required=True, label='ВД (мин.)')
    longitude_seconds = forms.DecimalField(min_value=0, max_value=60, required=True, label='ВД (сек.)')
    name_gwk = forms.IntegerField(label='Номер ГВК', required=False, widget=AdminTextInputWidget)
    name_drill = forms.CharField(label='Номер при бурении', required=False, widget=AdminTextInputWidget)
    name_subject = SimpleArrayField(
        forms.CharField(widget=AdminTextInputWidget), required=False,
        label='Номер присвоенный недропользователем',
        help_text='Можно указать несколько номеров через запятую', delimiter=',')

    class Meta:
        model = Wells
        fields = '__all__'
        widgets = {
            'geom': GeoWidget(
                attrs={
                    "default_lat": 54.5,
                    "default_lon": 36.28,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typo'].queryset = DictEntities.objects.filter(entity=1)
        self.fields['moved'].queryset = DictEntities.objects.filter(entity=3)

        if self.instance.pk and self.instance.extra:
            self.fields['name_gwk'].initial = self.instance.extra.get('name_gwk', '')
            self.fields['name_drill'].initial = self.instance.extra.get('name_drill', '')
            self.fields['name_subject'].initial = self.instance.extra.get('name_subject', '')

        if self.instance.pk and self.instance.geom:
            point = self.instance.geom
            lat_d, lat_m, lat_s = self._decimal_to_dms(point.y)
            lon_d, lon_m, lon_s = self._decimal_to_dms(point.x)
            self.initial['latitude_degrees'], self.initial['latitude_minutes'], self.initial[
                'latitude_seconds'] = lat_d, lat_m, lat_s
            self.initial['longitude_degrees'], self.initial['longitude_minutes'], self.initial[
                'longitude_seconds'] = lon_d, lon_m, lon_s

    def _decimal_to_dms(self, dec):
        d = int(dec)
        md = abs(dec - d) * 60
        m = int(md)
        sd = (md - m) * 60
        return [d, m, sd]

    def _dms_to_decimal(self, d, m, s):
        return d + float(m) / 60 + float(s) / 3600

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra = {
            'name_gwk': self.cleaned_data['name_gwk'],
            'name_drill': self.cleaned_data['name_drill'],
            'name_subject': self.cleaned_data['name_subject'],
        }
        lat = self._dms_to_decimal(self.cleaned_data['latitude_degrees'], self.cleaned_data['latitude_minutes'],
                                   self.cleaned_data['latitude_seconds'])
        lon = self._dms_to_decimal(self.cleaned_data['longitude_degrees'], self.cleaned_data['longitude_minutes'],
                                   self.cleaned_data['longitude_seconds'])
        instance.geom = Point(lon, lat)

        if commit:
            instance.save()
        return instance


class IntakesForm(forms.ModelForm):
    class Meta:
        model = Intakes
        fields = '__all__'
        widgets = {
            'geom': GeoWidget(
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
            'geom': GeoWidget(
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
        self.fields['typo'].queryset = DictEntities.objects.filter(entity=6)


class WellsRegimeForm(forms.ModelForm):
    class Meta:
        model = WellsRegime
        exclude = ('doc',)

    def __init__(self, *args, **kwargs):
        super(WellsRegimeForm, self).__init__(*args, **kwargs)


class WellsConstructionForm(forms.ModelForm):
    class Meta:
        model = WellsConstruction
        exclude = ('doc',)

    def __init__(self, *args, **kwargs):
        super(WellsConstructionForm, self).__init__(*args, **kwargs)
        self.fields['construction_type'].queryset = DictEntities.objects.filter(entity=8)


class WellsEfwForm(forms.ModelForm):
    class Meta:
        model = WellsEfw
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WellsEfwForm, self).__init__(*args, **kwargs)
        self.fields['type_efw'].queryset = DictEntities.objects.filter(entity=2)
        self.fields['method_measure'].queryset = DictEntities.objects.filter(entity=4)
        self.fields['date'].initial = timezone.now()


class WellsDepressionForm(forms.ModelForm):
    water_depth = forms.FloatField(label='Глубина воды, м', required=True)
    rate = forms.FloatField(label='Дебит, л/с', required=True)

    class Meta:
        model = WellsDepression
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WellsDepressionForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            self.fields['water_depth'].initial = kwargs['instance'].waterdepths.first().water_depth
            self.fields['rate'].initial = kwargs['instance'].rates.first().rate

    def save(self, *args, **kwargs):
        water_depth = self.cleaned_data.pop('water_depth')
        rate = self.cleaned_data.pop('rate')
        instance = super(WellsDepressionForm, self).save(*args, **kwargs)
        if water_depth:
            if self.instance.waterdepths.first():
                watinstance = self.instance.waterdepths.first()
                watinstance.water_depth = water_depth
                watinstance.save()
            else:
                self.instance.waterdepths.create(object_id=self.instance.pk, water_depth=water_depth)
        if rate:
            if self.instance.rates.first():
                rateinstance = self.instance.rates.first()
                rateinstance.rate = rate
                rateinstance.save()
            else:
                self.instance.rates.create(object_id=self.instance.pk, rate=rate)

        return instance


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BalanceForm, self).__init__(*args, **kwargs)
        self.fields['typo'].queryset = DictEntities.objects.filter(entity=5)


class WellsWaterDepthForm(forms.ModelForm):
    comments = forms.IntegerField(label='Примечания', required=False, widget=AdminTextInputWidget)

    class Meta:
        model = WellsWaterDepth
        exclude = ('content_type', 'object_id', 'content_object')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.extra:
            self.fields['comments'].initial = self.instance.extra.get('comments', '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra = {
            'comments': self.cleaned_data['comments'],
        }
        if commit:
            instance.save()
        return instance

