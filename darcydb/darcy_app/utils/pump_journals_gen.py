import datetime
import io
from decimal import Decimal

from django.core.files.base import ContentFile
from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from ..models import DocumentsPath, WellsAquifers, WellsDepression, WellsEfw, WellsLithology
from .doc_gen import PDF


class PumpJournal(PDF):
    def __init__(self, efw, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.efw = efw

    def create_info_data(self):
        field = self.get_fields()
        intake = self.get_intakes()
        # address = self.get_address()
        water_user = self.get_water_user()
        top, bot, lit, aq = self.create_aquifer_data()
        geophysics = self.get_geophysics_instance()
        depth_fact = ""
        if geophysics:
            depth_instance_new = geophysics.depths.first()
            if depth_instance_new:
                depth_fact = depth_instance_new.depth
        info = {
            "Месторождение": field.field_name if field else "",
            "Участок работ": intake.intake_name if intake else "",
            # "Местоположение": f"{address['country']}, {address['state']}, {address['county']}",
            "Недропользователь": water_user.name if water_user else "",
            "Адрес (почтовый) владельца скважины": water_user.position if water_user else "",
            "Целевой водоносный горизонт": aq.aquifer_index if aq else "",
            "Отметка устья скважины": f"{self.instance.head} м" if self.instance.head else "",
            "Глубина скважины": f"{depth_fact} м" if depth_fact else "",
            "Водовмещающие породы": lit,
            "Глубина кровли водоносного горизонта": f"{top} м" if top else "",
            "Глубина подошвы водоносного горизонта": f"{bot} м" if bot else "",
            "Даты проведения опыта": self.efw.date.date().strftime("%d.%m.%Y"),
            "Статический уровень воды на начало откачки": "",
            "Динамический уровень воды на конец откачки": "",
        }
        return info

    def get_instrumental_data(self):
        data = {
            "Тип, марка насоса": self.efw.pump_type or "",
            "Глубина установки насоса": self.efw.pump_depth or "",
            "Ёмкость мерного сосуда, м3": self.efw.vessel_capacity or "",
            "Время наполнения ёмкости, сек": self.time_to_seconds(self.efw.vessel_time)
            if self.efw.vessel_time
            else "",
            "Водомерное устройство": self.efw.rate_measure or "",
            "Наименование и марка уровнемера": self.efw.level_meter or "",
        }
        return data

    def get_pump_data(self):
        pump_data = []
        stat_level = self.efw.waterdepths.first().water_depth
        depr_qs = WellsDepression.objects.get(efw=self.efw)
        wat_depths = depr_qs.waterdepths.all()
        dyn_level = ""
        rate_fin = ""
        depression = ""
        for i, qs in enumerate(wat_depths):
            rate_inst = depr_qs.rates.filter(time_measure=qs.time_measure).first()
            depression = qs.water_depth - stat_level
            rate = ""
            if rate_inst:
                rate = rate_fin = round(rate_inst.rate * Decimal(3.6), 2)
            pump_data.append(
                (
                    (self.efw.date + qs.time_measure).date(),
                    int(qs.time_measure.total_seconds() // 3600),
                    int(qs.time_measure.total_seconds() % 3600 // 60),
                    qs.water_depth,
                    depression,
                    rate,
                    "",
                )
            )
            dyn_level = qs.water_depth
        return dyn_level, stat_level, rate_fin, round(rate_fin / depression, 2), depression, pump_data

    def get_recovery_data(self, dyn_wat):
        recovery_data = []
        efw_recovery = WellsEfw.objects.filter(
            well=self.efw.well, doc=self.efw.doc, type_efw__name="восстановление уровня"
        ).first()
        if efw_recovery:
            depr_qs = WellsDepression.objects.get(efw=efw_recovery)
            wat_depths = depr_qs.waterdepths.all()
            for qs in wat_depths:
                recovery = dyn_wat - qs.water_depth
                recovery_data.append(
                    (
                        (self.efw.date + qs.time_measure).date(),
                        int(qs.time_measure.total_seconds() // 3600),
                        int(qs.time_measure.total_seconds() % 3600 // 60),
                        qs.water_depth,
                        recovery,
                    )
                )
        return recovery_data

    def create_aquifer_data(self):
        aquifer = WellsAquifers.objects.filter(well=self.instance)
        lithology = WellsLithology.objects.filter(well=self.instance)
        aq_usage = self.get_aquifer_usage()
        if lithology.exists():
            top_elev = 0
            for i, hor in enumerate(lithology):
                aq = aquifer.filter(bot_elev__lte=hor.bot_elev).last()
                if not aq:
                    aq = aquifer.first()
                if aq_usage.filter(aquifer=aq.aquifer).exists():
                    description = self.form_lithology_description(hor)
                    return top_elev, hor.bot_elev, description, aq.aquifer
                top_elev = hor.bot_elev
        return ""

    def get_workers_signature(self):
        sign_list = [
            {"worker": "Кузьминов К. Г.", "sign": self.get_sign("pump1.png")},
            {"worker": "Здановский И. И.", "sign": self.get_sign("pump2.png")},
        ]
        return sign_list


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
    dyn_wat, stat_wat, rate, specific_rate, depression, pump_data = pdf.get_pump_data()
    info["Статический уровень воды на начало откачки"] = f"{stat_wat} м"
    info["Динамический уровень воды на конец откачки"] = f"{dyn_wat} м"
    info["Понижение на конец откачки"] = f"{depression} м"
    info["Дебит"] = f"{rate} м<sup>3</sup>/час"
    info["Удельный дебит"] = f"{specific_rate} м<sup>3</sup>/(час*м)"
    recovery_data = pdf.get_recovery_data(dyn_wat)
    sign_list = pdf.get_workers_signature()
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
        recovery_data=recovery_data,
        conclusions=efw.extra.get("comments", ""),
        sign_list=sign_list,
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
