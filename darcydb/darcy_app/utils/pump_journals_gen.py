import datetime
import io

from django.core.files.base import ContentFile
from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from ..models import DocumentsPath
from .doc_gen import PDF


class PumpJournal(PDF):
    pass


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
    rendered_html = template.render(
        logo=logo,
        year=datetime.datetime.now().year,
        watermark=watermark,
        sign=sign,
        stamp=stamp,
        well_id=well_id,
        type_well=f"{efw.well.typo.name[:-2]}ой".upper(),
        title_info=title,
    )
    output = io.BytesIO()
    html = HTML(string=rendered_html).render(stylesheets=[CSS("darcydb/darcy_app/utils/css/base.css")])
    html.write_pdf(target=output)
    name_pdf = f"Журнал_опытной_откачки_{efw}.pdf"
    document_path = DocumentsPath.objects.filter(doc=document).first()
    if document_path:
        document_path.delete()
    document_path = DocumentsPath(doc=document)
    output.seek(0)
    document_path.path.save(name_pdf, ContentFile(output.read()))
    document_path.save()
