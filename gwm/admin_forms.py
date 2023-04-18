from django.forms import Form, TextInput, Textarea, NumberInput, SelectMultiple, Select, ModelForm, ModelChoiceField, ModelMultipleChoiceField, MultipleChoiceField
from .models import *
from django import forms
from django.contrib.gis.geos import Point
from dal import autocomplete
from django.db import IntegrityError
from django.contrib.admin.widgets import FilteredSelectMultiple
from .api.views import *


__all__ = ['PoiForm', 'ObservationForm', 'spr_vzuForm', 'ChangeReasonForm']


class ChangeReasonForm(forms.Form):
    reason = forms.ModelChoiceField(queryset=spr_change_reason.objects.all())


class spr_vzuForm(ModelForm):
    class Meta:
        model = spr_vzu
        fields = '__all__'


class ObservationForm(ModelForm):
    class Meta:
        widgets = {
            'poi': autocomplete.ModelSelect2(
                url='gwm:api-poi-auto',
                forward=['vzu'],
                attrs={'data-html': True}),
        }

    def __init__(self, *args, **kwargs):
        super(ObservationForm, self).__init__(*args, **kwargs)
        self.fields['typo'].queryset = spr_type.objects.filter(apply_to__name='обследование')
        self.fields['state'].queryset = spr_type.objects.filter(apply_to__name='состояние скважины')


class PoiForm(ModelForm):

    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        required=True,
        label='lat[сш]град'
    )
    latitude_mm = forms.FloatField(
        min_value=0,
        max_value=60,
        required=True,
        label='lat[сш]мин'
    )
    latitude_ss = forms.FloatField(
        min_value=0,
        max_value=60,
        required=True,
        label='lat[сш]сек'
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        required=True,
        label='lon[вд]'
    )
    longitude_mm = forms.FloatField(
        min_value=0,
        max_value=60,
        required=True,
        label='lon[вд]мин'
    )
    longitude_ss = forms.FloatField(
        min_value=0,
        max_value=60,
        required=True,
        label='lon[вд]сек'
    )
    class Meta(object):
        model = Poi
        exclude = []
        widgets = {'point': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typo'].queryset = spr_type.objects.filter(apply_to__name='скважина')
        coordinates = self.initial.get('geom', None)
        if isinstance(coordinates, Point):
            self.initial['longitude'] = int(coordinates.x)
            self.initial['longitude_mm'] = int(coordinates.x % 1 * 60 )
            self.initial['longitude_ss'] = round( ((coordinates.x % 1 * 60) % 1 *60), 3)
            self.initial['latitude'] = int(coordinates.y)
            self.initial['latitude_mm'] = int(coordinates.y % 1 * 60 )
            self.initial['latitude_ss'] = round( ((coordinates.y % 1 * 60) % 1 *60), 3)

    def clean(self):
        data = super().clean()
        latitude = data.get('latitude')
        latitude_mm = data.get('latitude_mm')
        latitude_ss = data.get('latitude_ss')
        longitude = data.get('longitude')
        longitude_mm = data.get('longitude_mm')
        longitude_ss = data.get('longitude_ss')
        point = data.get('point')
        if latitude and longitude and not point:
            data['geom'] = Point(longitude+(longitude_mm/60)+(longitude_ss/3600), latitude+(latitude_mm/60)+(latitude_ss/3600))
        return data