import datetime

from darcydb.darcy_app.models import DictEntities, Documents, WellsEfw
from darcydb.darcy_app.utils.pump_journals_gen import generate_pump_journal


def run():
    code = DictEntities.objects.get(entity__name="тип документа", name="Журнал опытно-фильтрационных работ")
    efws = WellsEfw.objects.filter(well__intake__id=738, type_efw__name="откачки одиночные опытные")
    for qs in efws:
        doc_instance = qs.doc
        if not doc_instance:
            doc_instance = Documents.objects.create(
                name=f"Журнал опытной откачки из скважины №{qs.well.name} от {qs.date}",
                typo=code,
                creation_date=datetime.datetime.now().date(),
                object_id=qs.pk,
            )
            qs.doc = doc_instance
            qs.save()
        print(qs.well.name, doc_instance.pk)
        generate_pump_journal(qs, doc_instance)
