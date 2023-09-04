import os

from geopy.geocoders import Photon

from ..models import LicenseToWells, WaterUsersChange, WellsDrilledData, WellsGeophysics, WellsSample


class PDF:
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
    def get_sign():
        this_folder = os.path.dirname(os.path.abspath(__file__))
        img = "file://" + os.path.join(this_folder, "static", "sign.png")
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

    def __init__(self, instance, doc_instance):
        self.instance = instance
        self.doc_instance = doc_instance

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
            "дом 37 а строение 2, офис 0411.<br>Телефон: +7(495)968-04-82",
            "type_well": f"{self.instance.typo.name[:-2]}ой скважины<br> № {self.instance.pk}/"
            f"{'ГВК - ' + str(self.instance.extra['name_gwk']) if self.instance.extra.get('name_gwk') else ''}",
            "water_user": water_user.name if water_user else "",
            "user_info": water_user.position if water_user else "",
            "post": "Генеральный директор",
            "sign": "",
            "worker": "Р.М. Заманов",
        }
        return title_info

    def get_address(self):
        geolocator = Photon(user_agent="myGeocoder")
        address = geolocator.reverse(f"{self.instance.geom.y}, {self.instance.geom.x}").raw["properties"]
        return address

    def get_drilled_instance(self):
        return WellsDrilledData.objects.filter(well=self.instance).first()

    def get_geophysics_instance(self):
        return WellsGeophysics.objects.filter(well=self.instance, doc=self.doc_instance).first()

    def get_sample_instance(self):
        return WellsSample.objects.filter(well=self.instance).order_by("-date").first()
