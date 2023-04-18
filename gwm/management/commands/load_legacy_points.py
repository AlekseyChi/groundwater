from django.core.management.base import BaseCommand
from gwm.models import *
from legacy.models import *
from tqdm import tqdm


class Command(BaseCommand):
    help = 'help here'

    def handle(self, *args, **options):
        print('begin...')
        _pois = Kursk_wells.objects.filter(VZU='Зорининский')
        print(f'points: {_pois.count()}')
        e = 0
        if _pois.count():
            for p in tqdm(_pois):
                try:
                    poi = Poi.objects.create(
                        typo = spr_type.objects.get(name='скважина гидрогеологическая'),
                        vzu = spr_vzu.objects.get(name='МУП "Курскводоканал" в/з "Зоринский - 1"'),
                        nom = p.Well_Name,
                        gvk = p.GVK,
                        height = None,
                        geom = p.geom,
                        extra = {'note': p.prim, 'Well_type':p.Well_type, 'Aq_Name': p.Aq_Name, 'Aq_index': p.Aq_index, 'MPV':p.MPV, 'Well_cond': p.Well_cond, 'Intake_A': p.Intake_A, 'Intake_B':p.Intake_B, 'Intake_C1': p.Intake_C1}
                    )
                except Exception as err:
                    print(err)
                    e += 1
        if e:
            print(f'errors: {e}')
        else:
            print('OK. end!')

