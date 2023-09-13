import os
import re

import requests

from ..models import (
    LicenseToWells,
    WaterUsersChange,
    WellsAquiferUsage,
    WellsConstruction,
    WellsDrilledData,
    WellsGeophysics,
    WellsSample,
)


class PDF:
    @staticmethod
    def insert_tags(s, tag):
        tag_span = '<span style="font-size: 9pt">'

        def replacer(match):
            text = match.group(0)
            # Check if it's a lowercase character
            if text.islower():
                return f"{tag_span}{text}</span>"
            # Check if it's a hyphenated number
            elif "-" in text:
                return f"{tag_span}<{tag}>{text}</{tag}></span>"
            else:
                return f"{tag_span}<{tag}>{text}</{tag}></span>"

        return re.sub(r"\d+-\d+|\d+|[a-z]", replacer, s)

    @staticmethod
    def time_to_seconds(t):
        return (t.hour * 3600) + (t.minute * 60) + t.second

    @staticmethod
    def check_none(value):
        if value is not None:
            return value.name
        else:
            return ""

    @staticmethod
    def get_sign(name="Заманов Р.М..png"):
        this_folder = os.path.dirname(os.path.abspath(__file__))
        img = "file://" + os.path.join(this_folder, "static", "signatures", name)
        return img

    @staticmethod
    def get_stamp():
        this_folder = os.path.dirname(os.path.abspath(__file__))
        img = "file://" + os.path.join(this_folder, "static", "stamp.png")
        return img

    @staticmethod
    def get_logo():
        this_folder = os.path.dirname(os.path.abspath(__file__))
        img = "file://" + os.path.join(this_folder, "static", "M_Darcy_logo_rus.png")
        return img

    @staticmethod
    def get_watermark():
        this_folder = os.path.dirname(os.path.abspath(__file__))
        img = "file://" + os.path.join(this_folder, "static", "Darcy monogram.png")
        return img

    @staticmethod
    def decimal_to_dms(decimal_deg):
        degrees = int(decimal_deg)
        remainder_after_degrees = abs(decimal_deg - degrees) * 60
        minutes = int(remainder_after_degrees)
        remainder_after_minutes = (remainder_after_degrees - minutes) * 60
        seconds = round(remainder_after_minutes, 4)

        return f"{degrees}°{minutes}'{seconds}\""

    def __init__(self, instance, doc_instance):
        self.instance = instance
        self.doc_instance = doc_instance

    def form_lithology_description(self, lit):
        string_desc = [
            f"{self.check_none(lit.color)} {lit.rock}",
            self.check_none(lit.composition),
            self.check_none(lit.structure),
            self.check_none(lit.mineral),
            self.check_none(lit.secondary_change),
            self.check_none(lit.cement),
            self.check_none(lit.fracture),
            self.check_none(lit.weathering),
            self.check_none(lit.caverns),
            self.check_none(lit.inclusions),
        ]
        if lit.extra:
            if lit.extra.get("description"):
                string_desc.append(lit.extra["description"])
        return ", ".join([el for el in string_desc if el]).strip().capitalize()

    def get_fields(self):
        fields = self.instance.field
        return fields if fields else ""

    def get_intakes(self):
        intakes = self.instance.intake
        return intakes if intakes else ""

    def get_license(self):
        license_to_wells = LicenseToWells.objects.filter(well=self.instance).first()
        return license_to_wells.license if license_to_wells else None

    def get_water_user(self):
        licenses = self.get_license()
        if licenses:
            water_users_change = WaterUsersChange.objects.filter(license=licenses).first()
            return water_users_change.water_user if water_users_change else None

    def create_title(self):
        water_user = self.get_water_user()
        title_info = {
            "company": "Общество с ограниченной ответственностью «Дарси» (ООО «Дарси»)",
            "company_info": "Адрес: 117105, город Москва, Варшавское шоссе, "
            "дом 37 а строение 2, офис 0411.<br>Телефон: +7 (926) 359-76-53",
            "type_well": f"{self.instance.typo.name[:-2]}ой скважины<br> № {self.instance.name}/"
            f"{'ГВК - ' + str(self.instance.extra['name_gwk']) if self.instance.extra.get('name_gwk') else ''}",
            "water_user": water_user.name if water_user else "",
            "user_info": water_user.position if water_user else "",
            "post": "Генеральный директор",
            "sign": "",
            "worker": "Р.М. Заманов",
        }
        return title_info

    def get_address(self):
        lat, lon = self.instance.geom.y, self.instance.geom.x
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ru&zoom=15"
        try:
            result = requests.get(url=url)
            address = result.json()
            return address["address"]
        except Exception as e:
            return e

    def get_drilled_instance(self):
        return WellsDrilledData.objects.filter(well=self.instance).first()

    def get_geophysics_instance(self):
        return WellsGeophysics.objects.filter(well=self.instance).order_by("-date").first()

    def get_sample_instance(self):
        return WellsSample.objects.filter(well=self.instance).order_by("-date").first()

    def get_aquifer_usage(self):
        aquifers = WellsAquiferUsage.objects.filter(well=self.instance)
        return aquifers

    def create_construction_data(self):
        construction = WellsConstruction.objects.filter(well=self.instance)
        if construction.exists():
            for qs in construction:
                qs.date = qs.date if qs.date else "Нет сведений"
        return construction
