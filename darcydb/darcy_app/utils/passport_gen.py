import io

import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
from jinja2 import Environment, FileSystemLoader
from shapely.geometry import Point
from weasyprint import CSS, HTML


def create_schema(lat, lon):
    gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat)])
    gdf.crs = "EPSG:4326"
    gdf = gdf.to_crs("EPSG:3857")
    tilemapbase.start_logging()
    tilemapbase.init(create=True)
    x, y = gdf["geometry"][0].x, gdf["geometry"][0].y
    margin = 10000  # meters
    print(x, y)
    extent = tilemapbase.Extent.from_3857(x - margin, x + margin, y + margin, y - margin)
    dpi = 300
    fig, ax = plt.subplots(figsize=(500 / dpi, 450 / dpi), dpi=dpi)
    plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=100)
    plotter.plot(ax)

    ax.set_xlim(x - margin, x + margin)
    ax.set_ylim(y - margin, y + margin)
    ax.axis("off")
    gdf.plot(ax=ax, color="red", markersize=(1, 1))
    schema_pic = io.BytesIO()
    ax.figure.savefig("map.png", dpi=dpi, format="png")
    schema_pic.seek(0)
    # pic = image_compress(schema_pic, (400, 400))
    # return pic


class PDF:
    def __init__(self, instance):
        self.instance = instance

    def create_title(self):
        company = "Общество с ограниченной ответственностью</br>«Дарси»</br> (ООО «Дарси»)"
        company_info = (
            "Адрес: 117105, город Москва, Варшавское шоссе, дом 37 а "
            "строение 2, офис 0411.</br>Телефон: +7(495)968-04-82"
        )
        return company, company_info


def generate_passport(well):
    env = Environment(loader=FileSystemLoader("darcydb/darcy_app/utils/templates"))
    template = env.get_template("pass.html")
    pdf = PDF(well)
    company, company_info = pdf.create_title()

    rendered_html = template.render(
        company=company,
        company_info=company_info,
    )
    html = HTML(string=rendered_html).render(stylesheets=[CSS("darcydb/darcy_app/utils/css/base.css")])
    html.write_pdf("./1.pdf")
