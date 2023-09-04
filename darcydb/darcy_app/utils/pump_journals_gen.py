import datetime
import io
from decimal import Decimal

from django.core.files.base import ContentFile
from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from ..models import DocumentsPath, WellsDepression
from .doc_gen import PDF


class PumpJournal(PDF):
    def __init__(self, efw, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.efw = efw

    def create_info_data(self):
        field = self.get_fields()
        # address = self.get_address()
        water_user = self.get_water_user()
        aquifers = self.get_aquifer_usage()
        aquifers_str = ""
        if aquifers.exists():
            aquifers_str = ", ".join(aquifers.values_list("aquifer__aquifer_name", flat=True))
        info = {
            "Месторождение": field.field_name if field else "",
            # "Местоположение": f"{address['country']}, {address['state']}, {address['county']}",
            "Недропользователь": water_user.name if water_user else "",
            "Адрес (почтовый) владельца скважины": water_user.position if water_user else "",
            "Целевой водоносный горизонт": aquifers_str,
            "Отметка устья скважины": self.instance.head,
            "Глубина скважины": "",
            "Водовмещающие породы": "",
            "Глубина кровли водоносного горизонта": "",
            "Глубина подошвы водоносного горизонта": "",
            "Даты проведения опыта": "",
            "Статический уровень воды на начало откачки": "",
            "Динамический уровень воды на конец откачки": "",
        }
        return info

    def get_instrumental_data(self):
        data = {
            "Тип, марка насоса": self.efw.pump_type,
            "Глубина установки насоса": self.efw.pump_depth if self.efw.pump_depth else "",
            "Ёмкость мерного сосуда, м3": self.efw.vessel_capacity if self.efw.vessel_capacity else "",
            "Время наполнения ёмкости, сек": self.time_to_seconds(self.efw.vessel_time)
            if self.efw.vessel_time
            else "",
            "Водомерное устройство": self.efw.method_measure if self.efw.method_measure else "",
            "Наименование и марка уровнемера": self.efw.level_meter if self.efw.level_meter else "",
        }
        return data

    def get_pump_data(self):
        pump_data = []
        stat_level = self.efw.waterdepths.first().water_depth
        depr_qs = WellsDepression.objects.get(efw=self.efw)
        wat_depths = depr_qs.waterdepths.all()
        for i, qs in enumerate(wat_depths):
            rate_inst = depr_qs.rates.filter(time_measure=qs.time_measure).first()
            depression = qs.water_depth - stat_level
            rate = ""
            if rate_inst:
                rate = round(rate_inst.rate * Decimal(3.6), 2)
            pump_data.append(
                (
                    self.efw.date.date(),
                    qs.time_measure.hour,
                    qs.time_measure.minute,
                    qs.water_depth,
                    depression,
                    rate,
                    "",
                )
            )
        dyn_level = wat_depths.order_by("-time_measure").first()
        return dyn_level, stat_level, pump_data


def generate_pump_journal(efw, document):
    env = Environment(loader=FileSystemLoader("darcydb/darcy_app/utils/templates"))
    template = env.get_template("pump_journals/pump_journal.html")
    pdf = PumpJournal(efw, efw.well, document)
    logo = pdf.get_logo()
    watermark = pdf.get_watermark()
    sign = pdf.get_sign()
    stamp = pdf.get_stamp()
    well_id = f"{efw.well.pk}{'/ГВК' + str(efw.well.extra['name_gwk']) if efw.well.extra.get('name_gwk') else ''}"
    title = pdf.create_title()
    info = pdf.create_info_data()
    construction_data = pdf.create_construction_data()
    instrumental_data = pdf.get_instrumental_data()
    dyn_wat, stat_wat, pump_data = pdf.get_pump_data()
    rendered_html = template.render(
        doc_type="Журнал опытной откачки".upper(),
        logo=logo,
        year=datetime.datetime.now().year,
        watermark=watermark,
        sign=sign,
        stamp=stamp,
        well_id=well_id,
        type_well=f"{efw.well.typo.name[:-2]}ой".upper(),
        title_info=title,
        info=info,
        construction_data=construction_data,
        instrumental_data=instrumental_data,
        stat_wat=stat_wat,
        pump_data=pump_data,
        dyn_wat=dyn_wat,
        conclusions=efw.extra.get("comments", ""),
    )
    output = io.BytesIO()
    html = HTML(string=rendered_html).render(stylesheets=[CSS("darcydb/darcy_app/utils/css/base.css")])
    html.write_pdf(target=output)
    name_pdf = f"Журнал_опытной_откачки_{efw.well}-{efw.date.date()}.pdf"
    document_path = DocumentsPath.objects.filter(doc=document).first()
    if document_path:
        document_path.delete()
    document_path = DocumentsPath(doc=document)
    output.seek(0)
    document_path.path.save(name_pdf, ContentFile(output.read()))
    document_path.save()
