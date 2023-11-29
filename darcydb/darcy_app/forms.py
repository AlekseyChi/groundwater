import datetime

import numpy as np
import pandas as pd
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTimeWidget
from django.contrib.gis import forms
from django.contrib.gis.geos import Point
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError

from .models import (
    Balance,
    DictEntities,
    DictEquipment,
    Documents,
    Fields,
    Intakes,
    Wells,
    WellsAquifers,
    WellsAquiferUsage,
    WellsConstruction,
    WellsDepression,
    WellsEfw,
    WellsLithology,
    WellsRate,
    WellsRegime,
    WellsTemperature,
    WellsWaterDepth,
)


class GeoWidget(forms.OSMWidget):
    template_name = "gis/custom_layers.html"


# Wells
# -------------------------------------------------------------------------------
class WellsForm(forms.ModelForm):
    latitude_degrees = forms.IntegerField(min_value=-90, max_value=90, required=True, label="CШ (град.)")
    latitude_minutes = forms.IntegerField(min_value=0, max_value=60, required=True, label="CШ (мин.)")
    latitude_seconds = forms.DecimalField(min_value=0, max_value=60, required=True, label="CШ (сек.)")
    longitude_degrees = forms.IntegerField(min_value=-180, max_value=180, required=True, label="ВД (град.)")
    longitude_minutes = forms.IntegerField(min_value=0, max_value=60, required=True, label="ВД (мин.)")
    longitude_seconds = forms.DecimalField(min_value=0, max_value=60, required=True, label="ВД (сек.)")
    name_gwk = forms.IntegerField(label="Номер ГВК", required=False, widget=AdminTextInputWidget)
    name_drill = forms.CharField(label="Номер при бурении", required=False, widget=AdminTextInputWidget)
    name_subject = SimpleArrayField(
        forms.CharField(widget=AdminTextInputWidget),
        required=False,
        label="Номер присвоенный недропользователем",
        help_text="Можно указать несколько номеров через запятую",
        delimiter=",",
    )
    comments = forms.CharField(
        required=False, label="Дополнительные данные по скважине", widget=forms.Textarea(attrs={"rows": 2})
    )

    class Meta:
        model = Wells
        fields = "__all__"
        widgets = {
            "geom": GeoWidget(
                attrs={
                    "default_lat": 51.7,
                    "default_lon": 36.04,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["typo"].queryset = DictEntities.objects.filter(entity__name="тип скважины")
        self.fields["moved"].queryset = DictEntities.objects.filter(entity__name="уточнение местоположения")

        if self.instance.pk and self.instance.extra:
            self.fields["name_gwk"].initial = self.instance.extra.get("name_gwk", "")
            self.fields["name_drill"].initial = self.instance.extra.get("name_drill", "")
            self.fields["name_subject"].initial = self.instance.extra.get("name_subject", "")
            self.fields["comments"].initial = self.instance.extra.get("comments", "")

        if self.instance.pk and self.instance.geom:
            point = self.instance.geom
            lat_d, lat_m, lat_s = self._decimal_to_dms(point.y)
            lon_d, lon_m, lon_s = self._decimal_to_dms(point.x)
            self.initial["latitude_degrees"], self.initial["latitude_minutes"], self.initial["latitude_seconds"] = (
                lat_d,
                lat_m,
                lat_s,
            )
            self.initial["longitude_degrees"], self.initial["longitude_minutes"], self.initial["longitude_seconds"] = (
                lon_d,
                lon_m,
                lon_s,
            )

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
            "name_gwk": self.cleaned_data["name_gwk"],
            "name_drill": self.cleaned_data["name_drill"],
            "name_subject": self.cleaned_data["name_subject"],
            "comments": self.cleaned_data["comments"],
        }
        lat = self._dms_to_decimal(
            self.cleaned_data["latitude_degrees"],
            self.cleaned_data["latitude_minutes"],
            self.cleaned_data["latitude_seconds"],
        )
        lon = self._dms_to_decimal(
            self.cleaned_data["longitude_degrees"],
            self.cleaned_data["longitude_minutes"],
            self.cleaned_data["longitude_seconds"],
        )
        instance.geom = Point(lon, lat)

        if commit:
            instance.save()
        return instance


class WellsAquifersForm(forms.ModelForm):
    base_aquifer = forms.BooleanField(label="Целевой водоносный горизонт", required=False)

    class Meta:
        model = WellsAquifers
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if WellsAquiferUsage.objects.filter(well=self.instance.well, aquifer=self.instance.aquifer).exists():
                self.fields["base_aquifer"].initial = WellsAquiferUsage.objects.get(
                    well=self.instance.well, aquifer=self.instance.aquifer
                )

    def save(self, commit=True):
        instance = super().save(commit=False)
        well = instance.well
        aquifer = instance.aquifer
        base_aqua = self.cleaned_data.pop("base_aquifer")
        if base_aqua:
            if not WellsAquiferUsage.objects.filter(well=well, aquifer=aquifer).exists():
                WellsAquiferUsage.objects.create(well=well, aquifer=aquifer)
        else:
            if WellsAquiferUsage.objects.filter(well=well, aquifer=aquifer).exists():
                WellsAquiferUsage.objects.get(well=well, aquifer=aquifer).delete()
        if commit:
            instance.save()
        return instance


class WellsConstructionForm(forms.ModelForm):
    class Meta:
        model = WellsConstruction
        exclude = ("doc",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["construction_type"].queryset = DictEntities.objects.filter(
            entity__name="тип конструкции скважины"
        )


class WellsWaterDepthForm(forms.ModelForm):
    time_measure = forms.TimeField(widget=AdminTimeWidget(), label="Время замера", required=False)
    comments = forms.CharField(label="Примечания", max_length=300, widget=AdminTextInputWidget, required=False)

    class Meta:
        model = WellsWaterDepth
        exclude = ("content_type", "object_id", "content_object")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.extra:
            self.fields["comments"].initial = self.instance.extra.get("comments", "")

    def clean_time_measure(self):
        time_obj = self.cleaned_data["time_measure"]
        if time_obj:
            return datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra = {
            "comments": self.cleaned_data["comments"],
        }
        if commit:
            instance.save()
        return instance


class WellsTemperatureForm(forms.ModelForm):
    time_measure = forms.TimeField(widget=AdminTimeWidget(), label="Время замера")

    class Meta:
        model = WellsTemperature
        exclude = ("content_type", "object_id", "content_object")

    def clean_time_measure(self):
        time_obj = self.cleaned_data["time_measure"]
        return datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)


class WellsRateForm(forms.ModelForm):
    time_measure = forms.TimeField(widget=AdminTimeWidget(), label="Время замера")

    class Meta:
        model = WellsRate
        exclude = ("content_type", "object_id", "content_object")

    def clean_time_measure(self):
        time_obj = self.cleaned_data["time_measure"]
        return datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)


class WellsLithologyForm(forms.ModelForm):
    description = forms.CharField(label="Доп. описание", required=False)

    class Meta:
        model = WellsLithology
        fields = [
            "rock",
            "description",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rock"].queryset = DictEntities.objects.filter(entity__name="тип пород")
        self.fields["color"].queryset = DictEntities.objects.filter(entity__name="цвет пород")
        self.fields["composition"].queryset = DictEntities.objects.filter(entity__name="гран.состав")
        self.fields["structure"].queryset = DictEntities.objects.filter(entity__name="структура породы")
        self.fields["mineral"].queryset = DictEntities.objects.filter(entity__name="минеральный состав")
        self.fields["secondary_change"].queryset = DictEntities.objects.filter(
            entity__name="тип вторичного изменения пород"
        )
        self.fields["cement"].queryset = DictEntities.objects.filter(entity__name="тип цемента")
        self.fields["fracture"].queryset = DictEntities.objects.filter(entity__name="хар. трещиноватости пород")
        self.fields["weathering"].queryset = DictEntities.objects.filter(entity__name="степень выветрелости пород")
        self.fields["caverns"].queryset = DictEntities.objects.filter(entity__name="тип каверн")
        self.fields["inclusions"].queryset = DictEntities.objects.filter(entity__name="тип включения")

        if self.instance.pk and self.instance.extra:
            self.fields["description"].initial = self.instance.extra.get("description", "")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra = {
            "description": self.cleaned_data["description"],
        }
        if commit:
            instance.save()
        return instance


class WellsDepressionForm(forms.ModelForm):
    csv_file = forms.FileField(
        required=False,
        label="Импортировать данные с файла",
        help_text="CSV файл со следующими столбцами: 'time_measure', 'water_depth', 'rate'",
    )

    class Meta:
        model = WellsDepression
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        csv_file = self.cleaned_data.pop("csv_file")
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if csv_file:
                data = pd.read_csv(csv_file)
                if "time_measure" in data.columns:
                    data["time_measure"] = pd.to_timedelta(data["time_measure"], unit="m")
                else:
                    data = data.iloc[:, 0].str.split(";", expand=True)
                    data.columns = ["time_measure", "water_depth", "rate", *data.columns[3:]]
                    data["time_measure"] = pd.to_timedelta(data["time_measure"].astype(float), unit="m")
                data = data.replace(np.nan, None)
                for index, row in data.iterrows():
                    if row["time_measure"] is not None:
                        if row["water_depth"]:
                            instance.waterdepths.create(
                                time_measure=row["time_measure"], water_depth=float(row["water_depth"])
                            )
                        if row["rate"]:
                            instance.rates.create(time_measure=row["time_measure"], rate=float(row["rate"]))
        return instance


class DurationField(forms.Field):
    widget = forms.TextInput
    placeholder = "00:00:00"

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            hours, minutes, seconds = map(int, value.split(":"))
            return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            raise ValidationError("Неверный формат. Используйте часы:минуты:секунды")

    def prepare_value(self, value):
        if isinstance(value, datetime.timedelta):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return value


class WellsWaterDepthPumpForm(forms.ModelForm):
    class Meta:
        model = WellsWaterDepth
        exclude = ("content_type", "object_id", "content_object", "type_level")


class WellsEfwForm(forms.ModelForm):
    comments = forms.CharField(
        required=False, label="Примечания и рекомендации", widget=forms.Textarea(attrs={"rows": 2})
    )
    pump_time = DurationField(label="Продолжительность откачки", help_text="Часы:минуты:секунды")

    class Meta:
        model = WellsEfw
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type_efw"].queryset = DictEntities.objects.filter(entity__name="тип офр")
        self.fields["pump_type"].queryset = DictEquipment.objects.filter(
            typo__name="насос", typo__entity__name="тип оборудования"
        )
        self.fields["level_meter"].queryset = DictEquipment.objects.filter(
            typo__name="уровнемер", typo__entity__name="тип оборудования"
        )
        self.fields["rate_measure"].queryset = DictEquipment.objects.filter(
            typo__name="расходомер", typo__entity__name="тип оборудования"
        )
        self.fields["method_measure"].queryset = DictEntities.objects.filter(entity__name="способ замера дебита")
        # self.fields['date'].initial = timezone.now()

        if self.instance.pk and self.instance.extra:
            self.fields["comments"].initial = self.instance.extra.get("comments", "")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra = {
            "comments": self.cleaned_data["comments"],
        }
        if commit:
            instance.save()
        return instance


# Documents
# -------------------------------------------------------------------------------
class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Documents
        # fields = '__all__'
        exclude = ("content_type", "object_id", "content_object")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["typo"].queryset = DictEntities.objects.filter(entity__name="тип документа")


class IntakesForm(forms.ModelForm):
    class Meta:
        model = Intakes
        fields = "__all__"
        widgets = {
            "geom": GeoWidget(
                attrs={
                    "display_raw": True,
                    "default_lat": 51.7,
                    "default_lon": 36.04,
                },
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FieldsForm(forms.ModelForm):
    class Meta:
        model = Fields
        fields = "__all__"
        widgets = {
            "geom": GeoWidget(
                attrs={
                    "display_raw": True,
                    "default_lat": 51.7,
                    "default_lon": 36.04,
                },
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WellsRegimeForm(forms.ModelForm):
    class Meta:
        model = WellsRegime
        exclude = ("doc",)
        # widgets = {
        #     'well': forms.TextInput()
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["typo"].queryset = DictEntities.objects.filter(entity__name="тип подземных вод")


class DictEquipmentForm(forms.ModelForm):
    class Meta:
        model = DictEquipment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["typo"].queryset = DictEntities.objects.filter(entity__name="тип оборудования")
