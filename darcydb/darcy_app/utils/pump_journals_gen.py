import datetime
import io

from django.core.files.base import ContentFile
from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from ..models import DocumentsPath
from .doc_gen import PDF


class PumpJournal(PDF):
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


def generate_pump_journal(efw, document):
    env = Environment(loader=FileSystemLoader("darcydb/darcy_app/utils/templates"))
    template = env.get_template("pump_journals/pump_journal.html")
    pdf = PumpJournal(efw.well, document)
    logo = pdf.get_logo()
    watermark = pdf.get_watermark()
    sign = pdf.get_sign()
    stamp = pdf.get_stamp()
    well_id = f"{efw.well.pk}{'/ГВК' + str(efw.well.extra['name_gwk']) if efw.well.extra.get('name_gwk') else ''}"
    title = pdf.create_title()
    info = pdf.create_info_data()
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
