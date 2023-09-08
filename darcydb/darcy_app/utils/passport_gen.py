import base64
import datetime
import io
from decimal import Decimal

import geopandas as gpd
import markdown
import matplotlib.pyplot as plt
import tilemapbase
from django.core.files.base import ContentFile
from django.db.models import F, Q
from jinja2 import Environment, FileSystemLoader
from shapely.geometry import Point
from weasyprint import CSS, HTML

from ..models import DocumentsPath, WellsAquifers, WellsAquiferUsage, WellsDepression, WellsEfw, WellsLithology
from .doc_gen import PDF


class Passports(PDF):
    def create_position(self):
        licenses = self.get_license()
        water_user = self.get_water_user()
        address = self.get_address()
        position_info = {
            "Республика": address.get("country", ""),
            "Область": address.get("state", ""),
            "Район": address.get("county", ""),
            "Владелец скважины": water_user.name if water_user else "",
            "Адрес (почтовый) владельца скважины": water_user.position if water_user else "",
            "Координаты скважины": f"{round(self.instance.geom.y, 5)} С.Ш., {round(self.instance.geom.x, 5)} В.Д.",
            "Абсолютная отметка устья скважины": f"{self.instance.head} м",
            "Назначение скважины": f"{self.instance.typo.name[:-2]}ая",
            "Сведения о использовании": licenses.gw_purpose if licenses else "",
            "Лицензия на право пользования недрами": f"{licenses.name} от "
            f"{licenses.date_start.strftime('%d.%m.%Y')}"
            if licenses
            else "",
        }
        return position_info

    def get_attachments(self):
        aq = self.instance
        geophysics = self.get_geophysics_instance()
        chem = self.get_sample_instance()
        aq_attachments = geo_attachments = chem_attachments = []
        if aq.attachments.exists():
            aq_attachments = [item for attach in aq.attachments.all() for item in attach.get_base64_image()]
        if geophysics:
            geo_attachments = [item for attach in geophysics.attachments.all() for item in attach.get_base64_image()]
        if chem:
            chem_attachments = [item for attach in chem.attachments.all() for item in attach.get_base64_image()]
        return aq_attachments, geo_attachments, chem_attachments

    def create_drilled_base(self):
        drill = self.get_drilled_instance()
        drilled_info = {}
        nd = "Нет сведений"
        if drill:
            drilled_info["Буровая организация, выполнявшая бурение"] = drill.organization if drill.organization else nd
            drilled_info["Бурение начато"] = f"{drill.date_start.strftime('%d.%m.%Y')} г." if drill.date_start else nd
            drilled_info["Бурение окончено"] = f"{drill.date_end.strftime('%d.%m.%Y')} г." if drill.date_end else nd
        return drilled_info

    def get_pump_data(self, archive=True):
        efw_qs = (
            WellsEfw.objects.filter(well=self.instance)
            .exclude(type_efw__name="восстановление уровня")
            .order_by("-date")
        )
        if archive:
            efw = efw_qs.exclude(date__year=datetime.datetime.now().year).order_by("-date").first()
        else:
            efw = efw_qs.filter(date__year=datetime.datetime.now().year).order_by("-date").first()

        rate = ""
        depression = ""
        stat_wat = ""
        specific_rate = ""
        if efw:
            stat_wat = efw.waterdepths.first().water_depth
            depression_instance = WellsDepression.objects.get(efw=efw)
            rates = depression_instance.rates.first()
            dyn_wat = depression_instance.waterdepths.order_by("-time_measure").first()
            depression = dyn_wat.water_depth - stat_wat
            rate = rates.rate
            specific_rate = round(rate / depression, 2)
        return rate, depression, specific_rate, stat_wat

    def get_pump_complex(self):
        efw = (
            WellsEfw.objects.filter(well=self.instance)
            .exclude(type_efw__name__in=["откачки одиночные пробные", "восстановление уровня"])
            .order_by("-date")
            .first()
        )
        efw_data = {}
        levels = recommendations = ""
        if efw:
            stat_level = efw.waterdepths.first().water_depth
            dpr_instance = WellsDepression.objects.get(efw=efw)
            dyn_level = dpr_instance.waterdepths.all().order_by("-time_measure").first().water_depth
            rate = dpr_instance.rates.first().rate
            depression = dyn_level - stat_level
            specific_rate = round(rate / depression, 2)
            rate_hour = round(rate * Decimal(3.6), 2)
            rate_day = round(rate * Decimal(86.4), 2)
            efw_data = {
                "Дата производства откачки": efw.date.strftime("%d.%m.%Y"),
                "Продолжительность откачки": f"{efw.pump_time.total_seconds() // 3600} час.",
                "Водомерное устройство": efw.rate_measure or "",
                "Уровнемер, марка": efw.level_meter or "",
                "Тип и марка насоса": efw.pump_type or "",
                "Глубина установки насоса": f"{efw.pump_depth} м" if efw.pump_depth else "",
                "Дебит": f"{rate} л/сек; {rate_hour} м<sup>3</sup>/час; {rate_day} м<sup>3</sup>/сут",
                "Удельный дебит": f"{specific_rate} л/сек; "
                f"{round(specific_rate * Decimal(3.6), 2)} м<sup>3</sup>/(час*м)",
            }
            levels = (
                f"<strong>Статический уровень, м:</strong> {stat_level}; "
                f"<strong>Динамический уровень, м:</strong> {dyn_level}; "
                f"<strong>Понижение, м:</strong> {depression}"
            )
            recommendations = efw.extra.get("comments", "")
        return efw_data, levels, recommendations

    def get_test_pump(self):
        efw = WellsEfw.objects.filter(
            well=self.instance, doc=self.doc_instance, type_efw__name="откачки одиночные пробные"
        ).first()
        test_pump = []
        test_pump_info = {}
        if efw:
            stat_level = efw.waterdepths.first().water_depth
            depr_qs = WellsDepression.objects.get(efw=efw)
            wat_depths = depr_qs.waterdepths.all()
            for i, qs in enumerate(wat_depths):
                rate_inst = depr_qs.rates.filter(time_measure=qs.time_measure).first()
                depression = qs.water_depth - stat_level
                rate = ""
                specific_rate = ""
                if rate_inst:
                    rate = round(rate_inst.rate * Decimal(3.6), 2)
                    if depression:
                        specific_rate = round((rate / depression), 2)
                test_pump.append(
                    (
                        i + 1,
                        qs.time_measure,
                        qs.water_depth,
                        depression,
                        rate,
                        specific_rate,
                    )
                )
            last_time = wat_depths.last().time_measure
            # delta = datetime.timedelta(hours=last_time.hour, minutes=last_time.minute, seconds=last_time.second)
            test_pump_info.update(
                {
                    "Ёмкость мерного сосуда, м<sup>3</sup>": efw.vessel_capacity,
                    "Время наполнения ёмкости, сек": self.time_to_seconds(efw.vessel_time),
                    "Начало откачки": efw.date.strftime("%d.%m.%Y г. %H:%M"),
                    "Окончание откачки": (efw.date + last_time).strftime("%d.%m.%Y г. %H:%M"),
                    "Марка погружного насоса (компрессора)": efw.pump_type,
                }
            )
        return test_pump, test_pump_info

    def get_construction_formula(self, archive=True):
        construction = self.create_construction_data()
        cnstr_html = ""
        if construction:
            archive_date = (
                construction.filter(date__isnull=False).exclude(date__year=datetime.datetime.now().year).first()
            )
            if archive:
                if archive_date:
                    u_construction = construction.filter(date=archive_date.date)
                else:
                    u_construction = construction.filter(date__isnull=False).exclude(
                        date__year=datetime.datetime.now().year
                    )
            else:
                if archive_date:
                    u_construction = construction.exclude(date=archive_date.date)
                else:
                    u_construction = construction
            if u_construction.exists():
                cnstr_unit = " х ".join(
                    [
                        f"\\frac{{{qs.diameter}}}{{{str(qs.depth_from)+ '-' + str(qs.depth_till)}}}"
                        for qs in u_construction
                    ]
                )
                cnstr_html = markdown.markdown(
                    f"$`{cnstr_unit}`$",
                    extensions=[
                        "markdown_katex",
                    ],
                    extension_configs={
                        "markdown_katex": {
                            "no_inline_svg": True,
                            "insert_fonts_css": True,
                        },
                    },
                )
        return cnstr_html

    def create_archive_data(self):
        drill = self.get_drilled_instance()
        geophysics = self.get_geophysics_instance()
        construction_formula_old = self.get_construction_formula()
        construction_formula_new = self.get_construction_formula(archive=False)
        rate_old, depression_old, specific_rate_old, _ = self.get_pump_data()
        rate_new, depression_new, specific_rate_new, watdepth_new = self.get_pump_data(archive=False)
        depth_archive = ""
        depth_fact = ""
        watdepth_archive = ""
        if drill:
            depth_instance_old = drill.depths.first()
            watdepth_instance_old = drill.waterdepths.first()
            if depth_instance_old:
                depth_archive = depth_instance_old.depth
            if watdepth_instance_old:
                watdepth_archive = watdepth_instance_old.water_depth
        if geophysics:
            depth_instance_new = geophysics.depths.first()
            if depth_instance_new:
                depth_fact = depth_instance_new.depth
        archive_data = (
            (
                "Глубина, м",
                depth_archive,
                depth_fact,
            ),
            (
                "Конструкция, мм/м",
                construction_formula_old,
                construction_formula_new,
            ),
            (
                "Статический уровень, м",
                watdepth_archive,
                watdepth_new,
            ),
            (
                "Дебит, л/сек",
                rate_old,
                rate_new,
            ),
            (
                "Удельный дебит, л/(сек*м)",
                specific_rate_old,
                specific_rate_new,
            ),
            (
                "Понижение, м",
                depression_old,
                depression_new,
            ),
        )
        return archive_data

    def create_geophysics_data(self):
        geophysics = self.get_geophysics_instance()
        if geophysics:
            geophysics_data = {
                "Наименование организации": geophysics.organization,
                "Дата производства работ": geophysics.date.strftime("%d.%m.%Y"),
                "В скважине произведены следующие геофизические исследования": geophysics.researches,
                "Результаты геофизических исследований": geophysics.conclusion,
            }
            return geophysics_data

    def create_lithology(self):
        aquifer = WellsAquifers.objects.filter(well=self.instance)
        lithology = WellsLithology.objects.filter(well=self.instance)
        aq_usage = WellsAquiferUsage.objects.filter(well=self.instance)
        data = []
        if lithology.exists():
            top_elev = 0
            for i, hor in enumerate(lithology):
                aq = aquifer.filter(bot_elev__lte=hor.bot_elev).last()
                if not aq:
                    aq = aquifer.first()
                if aq_usage.filter(aquifer=aq.aquifer).exists():
                    comments = "Да"
                else:
                    comments = "Нет"
                description = self.form_lithology_description(hor)
                thick = hor.bot_elev - top_elev
                top_elev = hor.bot_elev
                data.append(
                    (
                        i + 1,
                        self.insert_tags(str(aq.aquifer.aquifer_index), "sub"),
                        description,
                        thick,
                        hor.bot_elev,
                        comments,
                    )
                )
        return data

    def create_sample_data(self):
        sample = self.get_sample_instance()
        sample_data = {}
        if sample:
            sample_data["Дата взятия пробы"] = sample.date.strftime("%d.%m.%Y")
            if sample.doc:
                sample_data.update(
                    {
                        "Дата производства анализа пробы": sample.doc.creation_date.strftime("%d.%m.%Y"),
                        "Организация, выполнившая анализ воды": sample.doc.org_executor,
                    }
                )
            sample_data["Протокол №"] = sample.name
        return sample_data

    def create_chem_conclusion(self):
        sample = self.get_sample_instance()
        if sample:
            chem = sample.chemvalues.filter(Q(chem_value__gte=F("parameter__chem_pdk")))
            if chem.exists():
                data = []
                for qs in chem:
                    chem_str = (
                        f"{qs.parameter.chem_name} "
                        f"{round(qs.chem_value, 2) if qs.chem_value >= 1 else qs.chem_value} "
                        f"{qs.parameter.chem_measure} "
                    )
                    row = (
                        f"{chem_str} "
                        f"({round(qs.chem_value / qs.parameter.chem_pdk, 2) if qs.parameter.chem_pdk else ''}ПДК)"
                    )
                    data.append(row)
                return ", ".join(data)

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
        margin = 3810  # meters
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

    def save(self):
        geophysics = self.get_geophysics_instance()
        if geophysics:
            geophysics.doc = self.doc_instance
            geophysics.save()


def generate_passport(well, document):
    env = Environment(loader=FileSystemLoader("darcydb/darcy_app/utils/templates"))
    template = env.get_template("passports/pass.html")
    pdf = Passports(well, document)
    logo = pdf.get_logo()
    watermark = pdf.get_watermark()
    sign = pdf.get_sign()
    stamp = pdf.get_stamp()
    well_id = f"{well.name}{'/ГВК' + str(well.extra['name_gwk']) if well.extra.get('name_gwk') else ''}"
    title = pdf.create_title()
    position_info = pdf.create_position()
    aq_attachments, geo_attachments, chem_attachments = pdf.get_attachments()
    schema = pdf.create_schema()
    drilled_info = pdf.create_drilled_base()
    drilled_data = pdf.create_archive_data()
    geo_journal = pdf.create_lithology()
    construction_data = pdf.create_construction_data()
    geophysics_data = pdf.create_geophysics_data()
    efr, levels, pump_recommendations = pdf.get_pump_complex()
    # test_pump, test_pump_info = pdf.get_test_pump()
    sample_data = pdf.create_sample_data()
    conclusion = pdf.create_chem_conclusion()
    extra_data = pdf.get_extra_data()
    sign_creator = pdf.get_sign("Мошин В.Е..png")
    rendered_html = template.render(
        doc_type="Паспорт".upper(),
        logo=logo,
        year=datetime.datetime.now().year,
        watermark=watermark,
        sign=sign,
        stamp=stamp,
        well_id=well_id,
        type_well=f"{well.typo.name[:-2]}ой".upper(),
        title_info=title,
        position_info=position_info,
        schema_pic=schema,
        drilled_header=drilled_info,
        drilled_data=drilled_data,
        geo_journal=geo_journal,
        construction_data=construction_data,
        geophysics_data=geophysics_data,
        efr=efr,
        levels=levels,
        pump_recommendations=pump_recommendations,
        # test_pump=test_pump,
        # test_pump_info=test_pump_info,
        sample_data=sample_data,
        conclusion=conclusion,
        extra_data=extra_data,
        aq_attachments=aq_attachments,
        geo_attachments=geo_attachments,
        chem_attachments=chem_attachments,
        sign_creator=sign_creator,
    )
    output = io.BytesIO()
    html = HTML(string=rendered_html).render(stylesheets=[CSS("darcydb/darcy_app/utils/css/base.css")])
    html.write_pdf(target=output)
    name_pdf = f"Паспорт_{well.name}.pdf"
    document_path = DocumentsPath.objects.filter(doc=document).first()
    if document_path:
        document_path.delete()
    document_path = DocumentsPath(doc=document)
    output.seek(0)
    document_path.path.save(name_pdf, ContentFile(output.read()))
    document_path.save()
    pdf.save()
