import base64
import datetime
import io
import os

import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
from geopy.geocoders import Photon
from jinja2 import Environment, FileSystemLoader
from shapely.geometry import Point
from weasyprint import CSS, HTML

from ..models import (
    DictEntities,
    LicenseToWells,
    WaterUsersChange,
    WellsConstruction,
    WellsDrilledData,
    WellsGeophysics,
)

passport_inst = DictEntities.objects.get(entity__name="тип документа", name="Паспорт скважины")


class PDF:
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

    def __init__(self, instance):
        self.instance = instance

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
            "company": "Общество с ограниченной ответственностью<br>«Дарси»<br> (ООО «Дарси»)",
            "company_info": "Адрес: 117105, город Москва, Варшавское шоссе, "
            "дом 37 а строение 2, офис 0411.<br>Телефон: +7(495)968-04-82",
            "type_well": f"{self.instance.typo.name[:-2]}ой скважины<br> № {self.instance.pk}/"
            f"{'ГВК - ' + str(self.instance.extra['name_gwk']) if self.instance.extra.get('name_gwk') else ''}",
            "water_user": water_user.name if water_user else "",
            "user_info": water_user.position if water_user else "",
            "post": "Генеральный директор",
            "sign": "",
            "worker": "Р.М. Заманов",
            "year": datetime.datetime.now().year,
        }
        return title_info

    def create_position(self):
        geolocator = Photon(user_agent="myGeocoder")
        address = geolocator.reverse(f"{self.instance.geom.y}, {self.instance.geom.x}").raw["properties"]
        licenses = self.get_license()
        water_user = self.get_water_user()
        position_info = {
            "Республика": address.get("country"),
            "Область": address.get("state"),
            "Район": address.get("county"),
            "Владелец скважины": water_user.name if water_user else "",
            "Адрес (почтовый) владельца скважины": water_user.position if water_user else "",
            "Координаты скважины": f"{self.instance.geom.y} С.Ш., {self.instance.geom.x} В.Д.",
            "Абсолютная отметка устья скважины": f"{self.instance.head} м",
            "Назначение скважины": f"{self.instance.typo.name[:-2]}ая",
            "Сведения о использовании": licenses.gw_purpose if licenses else "",
            "Лицензия на право пользования недрами": f"{licenses.name} от {licenses.date_start}" if licenses else "",
        }
        return position_info

    def create_drilled_base(self):
        drill = WellsDrilledData.objects.filter(well=self.instance).first()
        drilled_info = {}
        if drill:
            drilled_info["Буровая организация, выполнявшая бурение"] = (drill.organization,)
            drilled_info["Бурение окончено"] = f"{drill.date_end.year} г."

        return drilled_info

    def create_construction_data(self):
        construction = WellsConstruction.objects.filter(well=self.instance)
        if construction.exists():
            return construction

    def create_geophysics_data(self):
        geophysics = WellsGeophysics.objects.filter(well=self.instance, doc__typo=passport_inst).first()
        if geophysics:
            print(type(geophysics.date))
            geophysics_data = {
                "Наименование организации": geophysics.organization,
                "Дата производства работ": geophysics.date,  # .strftime("%d %b %y"),
                "В скважине произведены следующие геофизические исследования": geophysics.researches,
                "Результаты геофизических исследований": geophysics.conclusion,
            }
            return geophysics_data

    def get_extra_data(self):
        return self.instance.extra.get("comments")

    def create_schema(self):
        lat, lon = self.instance.geom.y, self.instance.geom.x
        gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat)])
        gdf.crs = "EPSG:4326"
        gdf = gdf.to_crs("EPSG:3857")
        tilemapbase.start_logging()
        tilemapbase.init(create=True)
        x, y = gdf["geometry"][0].x, gdf["geometry"][0].y
        margin = 5000  # meters
        extent = tilemapbase.Extent.from_3857(x - margin, x + margin, y + margin, y - margin)
        dpi = 100
        fig, ax = plt.subplots(figsize=(12, 12))
        plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
        plotter.plot(ax)
        ax.set_xlim(x - margin, x + margin)
        ax.set_ylim(y - margin, y + margin)
        ax.axis("off")
        gdf.plot(ax=ax, color="red", markersize=(80, 80))
        schema_pic = io.BytesIO()
        ax.figure.savefig(schema_pic, dpi=dpi, format="png")
        schema_pic.seek(0)
        schema = base64.b64encode(schema_pic.read()).decode("utf-8")
        return schema


def generate_passport(well):
    env = Environment(loader=FileSystemLoader("darcydb/darcy_app/utils/templates"))
    template = env.get_template("pass.html")
    pdf = PDF(well)
    logo = pdf.get_logo()
    watermark = pdf.get_watermark()
    well_id = f"{well.pk}{'/ГВК' + str(well.extra['name_gwk']) if well.extra.get('name_gwk') else ''}"
    title = pdf.create_title()
    position_info = pdf.create_position()
    schema = pdf.create_schema()
    drilled_info = pdf.create_drilled_base()
    construction_data = pdf.create_construction_data()
    geophysics_data = pdf.create_geophysics_data()
    extra_data = pdf.get_extra_data()
    rendered_html = template.render(
        logo=logo,
        watermark=watermark,
        well_id=well_id,
        type_well=f"{well.typo.name[:-2]}ой".upper(),
        title_info=title,
        position_info=position_info,
        schema_pic=schema,
        drilled_header=drilled_info,
        construction_data=construction_data,
        geophysics_data=geophysics_data,
        extra_data=extra_data,
    )
    html = HTML(string=rendered_html).render(stylesheets=[CSS("darcydb/darcy_app/utils/css/base.css")])
    html.write_pdf("./1.pdf")
