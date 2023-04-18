from django.core.management.base import BaseCommand
from gwm.models import *


class Command(BaseCommand):
    help = 'help here'

    def handle(self, *args, **options):
        print('begin...')
        '''
            import requests
            from pyairtable import *

            auth = 'keyQqTvfocrqB14k9'
            db = 'appuOo34978TcBy1H'
            tbl = 'tblQ97kqq3TacOOxz'

            if __name__ == '__main__':
                table = Table(auth, db, tbl)
                # берем первую запись
                pics = table.first()["fields"]["Приложение"]
                # сохраняем отдельно картинки
                for pic in pics:
                    print(f'save picture {pic["filename"]}...')
                    with requests.get(pic['url'], stream=True, timeout=(3.5, 7)) as r:
                        r.raise_for_status() # check if an error has occurred
                        with open(pic['filename'], 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192): 
                                # If you have chunk encoded response uncomment if
                                # and set chunk_size parameter to None.
                                #if chunk: 
                                f.write(chunk)
        '''
        print('end!')

