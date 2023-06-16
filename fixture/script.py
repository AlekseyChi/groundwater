import os
import json
import uuid
import psycopg2 as pg
import pandas as pd
import geopandas as gpd
import psycopg2.extras as extras
from psycopg2.extensions import AsIs

srid = 4326

os.chdir('./sources')

def replace_with_none(value):
    if pd.isna(value) or value is pd.NA:
        return None
    return value


def replace_by_dict(dfcol, entity):
    return dfcol.map(dict_entities[dict_entities['entity_id'] == entity].set_index('code')['id'])


# TODO: поменять user и password на локальные значения бд
def insert_to_db(df, table_name, multi=False, base=True):
    print(table_name)
    with pg.connect(database='darcy', user='user', password='password', host='db', port=5432) as conn:
        with conn.cursor() as cur:
            insert_data = []
            if base:
                column = ['extra', 'uuid', 'last_user_id']
            else:
                column = []
            for col in df.columns:
                if col != 'CODE' and col != 'geometry':
                    column.append(col)
            if 'geometry' in df.columns:
                column.append('geom')
            for index, row in df.iterrows():
                if 'geometry' in df.columns:
                    geom = row['geometry'].wkt
                    if multi:
                        geometry = f"ST_Multi(ST_GeomFromText('{geom}', {srid}))"
                    else:
                        geometry = f"ST_GeomFromText('{geom}', {srid})"
                    row = row[~row.index.isin(['geometry'])]
                data = {'data_source': 0}
                if 'CODE' in df.columns:
                    data.update({'name_gwk': int(row['CODE'])})
                    row = row[~row.index.isin(['CODE'])]
                extra = json.dumps(data)
                if base:
                    insert_data = (extra, str(uuid.uuid4()), 1,) + tuple(x for x in row.to_numpy())
                else:
                    insert_data = tuple(x for x in row.to_numpy())
                if 'geometry' in df.columns:
                    insert_data += (AsIs(geometry),)
                insert_data = [tuple(replace_with_none(item) for item in row) for row in [insert_data]]
                insert_sql = f"INSERT INTO {table_name} ({', '.join(column)}) VALUES %s"
                extras.execute_values(cur, insert_sql, insert_data)
            conn.commit()


def get_content_type(model):
    with pg.connect(database='darcy', user='user', password='password', host='db', port=5432) as conn:
        with conn.cursor() as cur:
            cur.execute('select id from django_content_type where model=%(model)s', {'model': model})
            id = cur.fetchone()
            return id[0]


aquifer_name = pd.read_csv('dict/_00001__202305032114.csv')
aquifer_index = pd.read_csv('dict/_00002__202305032115.csv')
aquifer_name['aquifer_name'] = aquifer_name['article']
aquifer_name = aquifer_name[['code', 'aquifer_name']]
aquifer_index['aquifer_index'] = aquifer_index['article']
aquifer_index = aquifer_index[['code', 'aquifer_index']]
aquifers = aquifer_name.set_index('code').join(aquifer_index.set_index('code'))
aquifers = aquifers.reset_index()
aquifers.columns = ['aquifer_id', 'aquifer_name', 'aquifer_index']

chem = pd.read_csv('dict/_00070__202305040057.csv')
chem['chem_name'] = chem['article']
chem = chem[['code', 'chem_name']]
chem.columns = ['chem_id', 'chem_name']

entities = pd.DataFrame({'name': ['тип скважины', 'тип офр', 'точность местоположения',
                                  'способы замера дебита', 'целевое назначение подземных вод', 'тип документа',
                                  'организация']})
entities['id'] = entities.reset_index().index + 1

rate = pd.read_csv('dict/_00066__202305041213.csv')
rate['name'] = rate['article']
rate['entity_id'] = 4
rate = rate.loc[1:, ['name', 'entity_id', 'code']]

ofr = pd.read_csv('dict/00018.csv')
ofr['name'] = ofr['article']
ofr['entity_id'] = 2
ofr = ofr[['name', 'entity_id', 'code']]

moved = pd.read_csv('dict/00098.csv')
moved['name'] = moved['article']
moved['entity_id'] = 3
moved = moved[['name', 'entity_id', 'code']]

well_type = pd.read_csv('dict/_00008__202305082102.csv')
well_type['name'] = well_type['article']
well_type['entity_id'] = 1
well_type = well_type[['name', 'entity_id', 'code']]

type_gw = pd.read_csv('dict/_00082__202305082037.csv')
type_gw['name'] = type_gw['article']
type_gw['entity_id'] = 5
type_gw = type_gw[['name', 'entity_id', 'code']]

dict_entities = pd.concat([well_type, ofr, moved, rate, type_gw], ignore_index=True, sort=False)
dict_entities['name'] = dict_entities['name'].apply(lambda x: x.lower())
dict_entities['id'] = dict_entities.reset_index().index + 1

# intakes
path = 'intakes'
table_name = 'intakes'
intakes = pd.DataFrame()
for file in os.listdir(path):
    if file.endswith('mif'):
        filename = os.path.join(path, file)
        df = gpd.GeoDataFrame.from_file(filename)
        df = df[df['geometry'].geom_type == 'Polygon']
        intakes = pd.concat([intakes, df])
intakes['id'] = intakes.reset_index().index + 1
intakes['CODE'] = intakes['CODE'].astype(int)
intakes = intakes[['id', 'CODE', 'NAME', 'geometry']]
intakes.columns = ['id', 'CODE', 'intake_name', 'geometry']

# fields
path = 'fields'
table_name = 'fields'
fields = pd.DataFrame()
for file in os.listdir(path):
    if file.endswith('mif'):
        filename = os.path.join(path, file)
        df = gpd.GeoDataFrame.from_file(filename)
        df = df[df['geometry'].geom_type == 'Polygon']
        fields = pd.concat([fields, df])
fields['id'] = fields.reset_index().index + 1
fields['CODE'] = fields['CODE'].astype(int)
fields = fields[['id', 'CODE', 'NAME', 'geometry']]
fields.columns = ['id', 'CODE', 'field_name', 'geometry']

# wells
path = 'wells'
table_name = 'wells'
wells = pd.DataFrame()
for file in os.listdir(path):
    if file.endswith('mif'):
        filename = os.path.join(path, file)
        df = gpd.GeoDataFrame.from_file(filename)
        wells = pd.concat([wells, df])
wells = wells.drop_duplicates(subset='CODE', keep="last")
wells['CODE'] = wells['CODE'].astype(int)
wells['id'] = wells.reset_index().index + 1
# wells.loc[wells['LAYER'] == 'Скважины режимные', 'typo_id'] = 2
# wells.loc[wells['LAYER'] == 'Скважины картировочные', 'typo_id'] = 5
# wells.loc[wells['LAYER'] == 'Скважины разведочные', 'typo_id'] = 3
# wells.loc[wells['LAYER'] == 'Скважины эксплуатационные', 'typo_id'] = 1
# wells.loc[wells['LAYER'] == 'Скважины режимные ОНС', 'typo_id'] = 2
# wells.loc[wells['LAYER'] == 'скважины альб-сеноманские', 'typo_id'] = 1
# wells.loc[wells['LAYER'] == 'скважины для воронежа', 'typo_id'] = 1
# wells.loc[wells['LAYER'] == 'Скважины радиологического опробования', 'typo_id'] = 2
# wells.loc[wells['LAYER'] == 'Скважины ликвидированные', 'typo_id'] = 1
# wells.loc[wells['LAYER'] == 'Скважины', 'typo_id'] = 1
wells = wells[['id', 'CODE', 'geometry']]
pdf = pd.read_csv('wells/ScvCatalog.csv')
pdf = pdf[['ScvID', 'ScvName', 'VZUID', 'kmpv', 'AbsOtmUstie', 'NaznachenieID', 'SposobKoordPrivID']]
column_name = ['CODE', 'name', 'intake_id', 'field_id', 'head', 'typo_id', 'moved_id']
pdf.columns = column_name
aquifer_well = pd.read_csv('data/ScvStatUr.csv')
aquifer_well = aquifer_well[['ScvID', 'GorID']]
aquifer_well["aquifer_id"] = aquifer_well['GorID']
wells = wells.set_index('CODE').join(pdf.set_index('CODE'), on='CODE')
aquifer_well = wells.join(aquifer_well.set_index('ScvID'), on='CODE')
wells['intake_id'] = wells['intake_id'].astype('Int64')
wells = wells.join(intakes[['CODE', 'id']].set_index('CODE'), on='intake_id', rsuffix='_intakes')
wells['intake_id'] = wells['id_intakes'].astype('Int64')
wells['field_id'] = wells['field_id'].astype('Int64')
wells = wells.join(fields[['CODE', 'id']].set_index('CODE'), on='field_id', rsuffix='_field')
wells['field_id'] = wells['id_field'].astype('Int64')
wells = wells.reset_index()
wells = wells[['id', 'name', 'intake_id', 'field_id', 'head', 'typo_id', 'moved_id', 'geometry', 'CODE']]
wells[~wells['moved_id'].isna()]
wells['moved_id'] = replace_by_dict(wells['moved_id'], 3)
wells['typo_id'] = wells['typo_id'].fillna(1)
wells['typo_id'] = replace_by_dict(wells['typo_id'], 1)
wells = wells.drop_duplicates(keep='last')
aquifer_well = aquifer_well[['id', 'aquifer_id']][~aquifer_well['aquifer_id'].isna()].drop_duplicates(keep='last')
aquifer_well = aquifer_well.rename(columns={'id': 'well_id'})

# wells_auifers
wells_aquifers = pd.read_csv('data/ScvLitolog.csv')
wells_aquifers = wells_aquifers[['ScvID', 'GorID', 'PodoshvaDeep']]
wells_aquifers.columns = ['CODE', 'aquifer_id', 'bot_elev']
wells_aquifers = wells_aquifers.join(wells.set_index('CODE'), on='CODE', lsuffix='_geo')[
    ['id', 'aquifer_id', 'bot_elev']]
wells_aquifers.columns = ['well_id', 'aquifer_id', 'bot_elev']
wells_aquifers = wells_aquifers.groupby(['well_id', 'aquifer_id']).agg({'bot_elev': 'max'}).reset_index()

# wells_waterdepth
wells_wat_init = pd.read_csv('data/ScvRegimeUroven.csv')
wells_wat2020 = pd.read_csv('data/uroven_2020.csv')
wells_wat2021 = pd.read_csv('data/uroven_20201.csv')
wells_wat = pd.concat([wells_wat_init, wells_wat2020, wells_wat2021])
wells_wat = wells_wat[['ScvID', 'DateMeasure', 'Uroven']]
wells_wat.columns = ['CODE', 'date', 'water_depth']
wells_wat = wells_wat.join(wells.set_index('CODE'), on='CODE', lsuffix='_geo')[['id', 'date', 'water_depth']]
wells_wat = wells_wat[~wells_wat['id'].isna()]
wells_wat = wells_wat[~wells_wat['water_depth'].isna()]
wells_wat = wells_wat.drop_duplicates(subset=['id', 'date'], keep="last")
wells_wat['content_type_id'] = get_content_type('wellsregime')
wells_wat['object_id'] = wells_wat.reset_index().index + 1
wells_regime = wells_wat[['object_id', 'id', 'date']]
wells_regime.columns = ['id', 'well_id', 'date']
wells_water = wells_wat[['content_type_id', 'object_id', 'water_depth']]

# wells_chem
wells_sample = pd.read_csv('data/ChemProba.csv')
wells_prot = pd.read_csv('data/ChemAnalysis.csv')
wells_comp = pd.read_csv('data/ChemAnalysisComponent.csv')
wells_comp.head()
wells_chem = wells_sample.join(wells_prot.set_index('ProbaNumber'), on='ProbaNumber')
wells_chem = wells_chem.join(wells.set_index('CODE'), on="IDPN")
wells_chem = wells_chem[['ProbaNumber', 'id', 'DateOtbor', 'AnalysisNumber']][~wells_chem['AnalysisNumber'].isna()]
wells_chem['id_chem'] = wells_chem.reset_index().index + 1
wells_chem = wells_comp.join(wells_chem[~wells_chem['id'].isna()].set_index('AnalysisNumber'), on='AnalysisNumber')
wells_chem = wells_chem[~wells_chem['id'].isna()]
wells_chem = wells_chem.loc[1:, ~wells_chem.columns.isin(['AnalysisNumber'])]
wells_chem['object_id'] = wells_chem['id_chem']
wells_chem['content_type_id'] = get_content_type('wellssample')
wells_chem.columns = ['parameter', 'chem_value', 'name', 'well_id', 'date', 'id_chem', 'object_id', 'content_type_id']
wells_chem = wells_chem.drop_duplicates(subset=['well_id', 'date', 'parameter'], keep='first')
wells_chem = wells_chem[~wells_chem['date'].isna()]
wells_sample_tab = wells_chem[['id_chem', 'well_id', 'date', 'name']]
wells_chem_tab = wells_chem[['object_id', 'content_type_id', 'parameter', 'chem_value']]
wells_sample_tab = wells_sample_tab.drop_duplicates(subset=['well_id', 'date'], keep='first')
wells_sample_tab['name'] = wells_sample_tab['name'].astype('Int64').astype(str)
wells_sample_tab = wells_sample_tab.rename(columns={'id_chem': 'id'})
wells_sample_tab = wells_sample_tab[~wells_sample_tab['well_id'].isna()]

balance = pd.read_csv('data/RGWLayer.csv')
balance = balance[['kmpv', 'kgor', 'zapA', 'zapB', 'zapC1', 'zapC2', 'nazg']]
balance = balance.join(fields[['id', 'CODE']].set_index('CODE'), on='kmpv')
balance = balance[~balance['id'].isna()]
balance['content_type_id'] = get_content_type('fields')
balance = balance[['id', 'kgor', 'zapA', 'zapB', 'zapC1', 'zapC2', 'nazg', 'content_type_id']]
balance.columns = ['object_id', 'aquifer_id', 'a', 'b', 'c1', 'c2', 'typo_id', 'content_type_id']
balance['typo_id'] = 0
balance['typo_id'] = replace_by_dict(balance['typo_id'], 5)

dict_entities_main = dict_entities[['id', 'name', 'entity_id']]

table_dfs = [
    (entities, 'entities', None), (dict_entities_main, 'dict_entities', None), (intakes, 'intakes', {'multi': True}),
    (aquifers, 'aquifer_codes', {'base': False}), (chem, 'chem_codes', {'base': False}),
    (fields, 'fields', {'multi': True}), (wells, 'wells', None),
    (aquifer_well, 'wells_aquifer_usage', None),
    (wells_aquifers, 'wells_aquifers', None),
    (wells_regime, 'wells_regime', None), (wells_water, 'wells_water_depth', None),
    (wells_sample_tab, 'wells_sample', None), (wells_chem_tab, 'wells_chem', None),
    (balance, 'fields_balance', None)
]
for i, j, kw in table_dfs:
    if kw:
        insert_to_db(i, j, **kw)
    else:
        insert_to_db(i, j)
