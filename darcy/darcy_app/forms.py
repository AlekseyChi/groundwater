from django.contrib.gis import forms
from django.contrib.admin.widgets import AdminTextInputWidget
from .models import Wells


class WellsForm(forms.ModelForm):
    class Meta:
        model = Wells
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
        super(WellsForm, self).__init__(*args, **kwargs)
        self.fields['typo'].queryset = DictEntities.objects.filter(entity=1)
        self.fields['well_name_gwk'] = forms.IntegerField(widget=AdminTextInputWidget)
        self.fields['well_name_drill'] = forms.CharField(widget=AdminTextInputWidget)

        if self.instance.pk and self.instance.data:
            self.fields['well_name_gwk'].initial = self.instance.data.get('well_name_gwk', '')
            self.fields['well_name_drill'].initial = self.instance.data.get('well_name_drill', '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra = {
            'well_name_gwk': self.cleaned_data['well_name_gwk'],
            'well_name_drill': self.cleaned_data['well_name_drill'],
        }
        if commit:
            instance.save()
        return instance
