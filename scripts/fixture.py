import os
import time

import geopandas as gpd
import numpy as np
import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.utils import timezone
from shapely.geometry import MultiPolygon

from darcydb.darcy_app.models import (
    AquiferCodes,
    Balance,
    ChemCodes,
    DictDocOrganizations,
    DictEntities,
    DictEquipment,
    Entities,
    Fields,
    Intakes,
    License,
    LicenseToWells,
    WaterUsers,
    WaterUsersChange,
    Wells,
    WellsAquifers,
    WellsAquiferUsage,
    WellsChem,
    WellsCondition,
    WellsConstruction,
    WellsDepression,
    WellsDepth,
    WellsDrilledData,
    WellsEfw,
    WellsLithology,
    WellsRate,
    WellsRegime,
    WellsSample,
    WellsTemperature,
    WellsWaterDepth,
)
from darcydb.users.models import User

data_source = {"data_source": 0}


def check_null(row):
    value = None
    if row:
        value = DictEntities.objects.filter(extra__old_code=row).first()
    return value


def import_csv_to_model(file_path="", entity_name=None):
    # Read CSV into a DataFrame
    if type(file_path) is pd.DataFrame:
        df = file_path
    else:
        df = pd.read_csv(file_path)
        df = df.drop_duplicates(subset="article", keep="first")
    for index, row in df.iterrows():
        code = row["code"]
        name = row["article"]

        entity = Entities.objects.get(name=entity_name)
        extra = {"old_code": code}
        dict_entity = DictEntities(name=name, entity=entity, extra=extra)
        dict_entity.save()


def run():
    st = time.time()
    tables = [
        "wells",
        "intakes",
        "fields",
        "wells_water_depth",
        "wells_condition",
        "wells_chem",
        "wells_construction",
        "wells_depth",
        "wells_sample",
        "wells_regime",
        "wells_drilled_data",
        "wells_lithology",
        "wells_aquifers",
        "wells_aquifer_usage",
        "entities",
        "dict_entities",
        "aquifer_codes",
        "chem_codes",
        "fields_balance",
        "water_users",
        "license",
        "license_to_wells",
        "wells_efw",
        "wells_depression",
        "wells_rate",
        "wells_temperature",
        "water_users_change",
        "dict_equipment",
        "dict_doc_organization",
    ]
    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
    entities = [
        "тип документа",
        "тип скважины",
        "тип офр",
        "тип конструкции скважины",
        "способ замера дебита",
        "тип подземных вод",
        "тех.состояние скважины",
        "уточнение местоположения",
        "тип пород",
        "цвет пород",
        "гран.состав",
        "структура породы",
        "минеральный состав",
        "тип вторичного изменения пород",
        "тип цемента",
        "хар. трещиноватости пород",
        "степень выветрелости пород",
        "тип каверн",
        "тип включения",
        "тип оборудования",
    ]
    for entity in entities:
        Entities(name=entity).save()
    print("entities")

    import_csv_to_model("./scripts/sources/dictionaries/doc_types.csv", "тип документа")
    import_csv_to_model("./scripts/sources/dictionaries/_00008__202305082102.csv", "тип скважины")
    import_csv_to_model("./scripts/sources/dictionaries/00018.csv", "тип офр")
    import_csv_to_model("./scripts/sources/dictionaries/_00064__202305291500.csv", "тип конструкции скважины")
    import_csv_to_model("./scripts/sources/dictionaries/_00066__202305041213.csv", "способ замера дебита")
    import_csv_to_model("./scripts/sources/dictionaries/_00082__202305082037.csv", "тип подземных вод")
    import_csv_to_model("./scripts/sources/dictionaries/00017.csv", "тех.состояние скважины")
    import_csv_to_model("./scripts/sources/dictionaries/00098.csv", "уточнение местоположения")
    import_csv_to_model("./scripts/sources/dictionaries/00020.csv", "тип пород")
    import_csv_to_model("./scripts/sources/dictionaries/00022.csv", "цвет пород")
    import_csv_to_model("./scripts/sources/dictionaries/00023.csv", "гран.состав")
    import_csv_to_model("./scripts/sources/dictionaries/00024.csv", "структура породы")
    import_csv_to_model("./scripts/sources/dictionaries/00026.csv", "минеральный состав")
    import_csv_to_model("./scripts/sources/dictionaries/00027.csv", "тип вторичного изменения пород")
    import_csv_to_model("./scripts/sources/dictionaries/00028.csv", "тип цемента")
    import_csv_to_model("./scripts/sources/dictionaries/00034.csv", "хар. трещиноватости пород")
    import_csv_to_model("./scripts/sources/dictionaries/00035.csv", "степень выветрелости пород")
    import_csv_to_model("./scripts/sources/dictionaries/00037.csv", "тип каверн")
    import_csv_to_model("./scripts/sources/dictionaries/00038.csv", "тип включения")
    df_eq = pd.DataFrame(
        data=[
            (
                1,
                "насос",
            ),
            (
                2,
                "уровнемер",
            ),
        ],
        columns=["code", "article"],
    )
    import_csv_to_model(df_eq, entity_name="тип оборудования")
    print("dict_entities")

    aquifer_name = pd.read_csv("./scripts/sources/dictionaries/_00001__202305032114.csv")
    aquifer_index = pd.read_csv("./scripts/sources/dictionaries/_00002__202305032115.csv")
    aquifer_name["aquifer_name"] = aquifer_name["article"]
    aquifer_name = aquifer_name[["code", "aquifer_name"]]
    aquifer_index["aquifer_index"] = aquifer_index["article"]
    aquifer_index = aquifer_index[["code", "aquifer_index"]]
    aquifers = aquifer_name.set_index("code").join(aquifer_index.set_index("code"))
    aquifers = aquifers.reset_index()
    aquifers.columns = ["aquifer_id", "aquifer_name", "aquifer_index"]
    aquifers = aquifers.replace(np.nan, None)

    chem = pd.read_csv("./scripts/sources/dictionaries/_00070__202305040057.csv")
    chem_pdk = pd.read_csv("./scripts/sources/dictionaries/ChemPDKComponent.csv")
    chem_pdk = chem_pdk.drop_duplicates(subset="ComponentCode", keep="first")
    chems = chem.set_index("code").join(chem_pdk.set_index("ComponentCode"))
    chems = chems.reset_index()
    chems = chems.replace(np.nan, None)

    for index, row in aquifers.iterrows():
        AquiferCodes(
            aquifer_id=row["aquifer_id"], aquifer_name=row["aquifer_name"], aquifer_index=row["aquifer_index"]
        ).save()
    print("aquifer_codes")

    for index, row in chems.iterrows():
        ChemCodes(
            chem_id=row["code"],
            chem_name=row["article"],
            chem_pdk=row["ValuePDKTo"],
        ).save()
    print("chem_codes")

    intakes = gpd.read_file("./scripts/sources/geometry/intake.mif")
    intakes["geometry"] = intakes["geometry"].apply(lambda x: MultiPolygon([x]) if x.geom_type == "Polygon" else x)
    for index, row in intakes.iterrows():
        if row["geometry"].geom_type == "Polygon" or row["geometry"].geom_type == "MultiPolygon":
            geom = GEOSGeometry(row["geometry"].wkt)
            extra = {"name_gwk": int(row["CODE"])}
            Intakes(intake_name=row["NAME"], geom=geom, extra=extra).save()
    print("intakes")

    fields = gpd.read_file("./scripts/sources/geometry/fields.mif")
    fields = fields.dissolve(by="NAME").reset_index()
    fields["geometry"] = fields["geometry"].apply(lambda x: MultiPolygon([x]) if x.geom_type == "Polygon" else x)
    for index, row in fields.iterrows():
        if row["geometry"].geom_type == "Polygon" or row["geometry"].geom_type == "MultiPolygon":
            extra = {"name_gwk": int(row["CODE"])}
            geom = GEOSGeometry(row["geometry"].wkt)
            Fields(field_name=row["NAME"], geom=geom, extra=extra).save()
    print("fields")

    path = "./scripts/sources/geometry"
    wells = pd.DataFrame()
    for file in os.listdir(path):
        if "well" in file and file.endswith("mif"):
            filename = os.path.join(path, file)
            df = gpd.read_file(filename)
            wells = pd.concat([wells, df])
    wells["CODE"] = wells["CODE"].astype(int)
    catalog = pd.read_csv("./scripts/sources/data/ScvCatalog.csv")
    wells = wells.set_index("CODE").join(catalog.set_index("ScvID"))
    wells = wells.reset_index()
    wells = wells.replace(np.nan, None)
    wells = wells.drop_duplicates(subset="CODE", keep="last")
    for index, row in wells.iterrows():
        if row["NaznachenieID"]:
            typo = DictEntities.objects.get(entity__name="тип скважины", extra__old_code=row["NaznachenieID"])
        else:
            typo = DictEntities.objects.get(entity__name="тип скважины", extra__old_code=2)
        if row["SposobKoordPrivID"]:
            moved = DictEntities.objects.get(
                entity__name="уточнение местоположения", extra__old_code=row["SposobKoordPrivID"]
            )
        else:
            moved = None
        intake_inst = Intakes.objects.filter(extra__name_gwk=row["VZUID"]).first()
        field_inst = Fields.objects.filter(extra__name_gwk=row["kmpv"]).first()
        extra = {"name_gwk": int(row["CODE"])}
        geom = GEOSGeometry(row["geometry"].wkt)
        Wells(
            name=row["NAME"],
            typo=typo,
            moved=moved,
            head=row["AbsOtmUstie"],
            intake=intake_inst if intake_inst else None,
            field=field_inst if field_inst else None,
            geom=geom,
            extra=extra,
        ).save()
    print("wells")

    wells = Wells.objects.only("pk", "extra")
    wells_dict = {well.extra["name_gwk"]: well for well in wells}
    batch_size = 50000
    user = User.objects.get(id=1)

    well_usage = pd.read_csv("./scripts/sources/data/ScvStatUr.csv")
    well_usage = well_usage.drop_duplicates(subset=["ScvID", "GorID"], keep="first")[~well_usage["GorID"].isna()]
    for index, row in well_usage.iterrows():
        well = wells_dict.get(row["ScvID"])
        aquifer = AquiferCodes.objects.get(aquifer_id=row["GorID"])
        if well:
            WellsAquiferUsage(well=well, aquifer=aquifer).save()

    wells_aquifers_all = pd.read_csv("./scripts/sources/data/ScvLitolog.csv")
    wells_aquifers_all = wells_aquifers_all.replace(np.nan, None)
    wells_aquifers = wells_aquifers_all[["ScvID", "GorID", "PodoshvaDeep"]]
    wells_aquifers.columns = ["well", "aquifer", "bot_elev"]
    wells_aquifers = wells_aquifers.groupby(["well", "aquifer"]).agg({"bot_elev": "max"}).reset_index()
    wa_instances = []
    for index, row in wells_aquifers.iterrows():
        well = wells_dict.get(row["well"])
        aquifer = AquiferCodes.objects.filter(aquifer_id=row["aquifer"]).first()
        user = User.objects.get(id=1)
        if well and aquifer:
            wa_instances.append(
                WellsAquifers(well=well, aquifer=aquifer, bot_elev=row["bot_elev"], extra=data_source, last_user=user)
            )
    WellsAquifers.objects.bulk_create(wa_instances)
    print("wells_aquifers")

    wells_lithology = wells_aquifers_all[
        [
            "ScvID",
            "Poroda",
            "Color",
            "GranSost",
            "Structure",
            "Mineral",
            "SecChange",
            "SostCem",
            "CharTresch",
            "StepVivetr",
            "Kavernosn",
            "Vkluchenia",
            "PodoshvaDeep",
        ]
    ]

    wells_lithology = wells_lithology.drop_duplicates(subset=["ScvID", "Poroda", "PodoshvaDeep"], keep="last")
    wl_instances = []
    for index, row in wells_lithology.iterrows():
        well = wells_dict.get(row["ScvID"])
        rock = DictEntities.objects.filter(extra__old_code=row["Poroda"]).first()
        user = User.objects.get(id=1)
        if well and rock:
            wl_instances.append(
                WellsLithology(
                    well=well,
                    rock=rock,
                    color=check_null(row["Color"]),
                    composition=check_null(row["GranSost"]),
                    structure=check_null(row["Structure"]),
                    mineral=check_null(row["Mineral"]),
                    secondary_change=check_null(row["SecChange"]),
                    cement=check_null(row["SostCem"]),
                    fracture=check_null(row["CharTresch"]),
                    weathering=check_null(row["StepVivetr"]),
                    caverns=check_null(row["Kavernosn"]),
                    inclusions=check_null(row["Vkluchenia"]),
                    bot_elev=row["PodoshvaDeep"],
                    extra=data_source,
                    last_user=user,
                )
            )
    WellsLithology.objects.bulk_create(wl_instances)
    print("wells_lithology")

    wells_wat_init = pd.read_csv("./scripts/sources/data/ScvRegimeUroven.csv")
    wells_wat2020 = pd.read_csv("./scripts/sources/data/uroven_2020.csv")
    wells_wat2021 = pd.read_csv("./scripts/sources/data/uroven_20201.csv")
    temperature = pd.read_csv("./scripts/sources/data/ScvRegimeTemperatura.csv")
    temperature = temperature[~temperature["Temperatura"].isna()]
    wells_wat = pd.concat([wells_wat_init, wells_wat2020, wells_wat2021])
    merged_df = pd.merge(wells_wat, temperature, on=["ScvID", "DateMeasure"], how="left")

    # Drop duplicates
    merged_df = merged_df.drop_duplicates(subset=["ScvID", "DateMeasure"])
    merged_df = merged_df.replace(np.nan, None)

    merged_df["date_time"] = pd.to_datetime(merged_df["DateMeasure"], format="%m/%d/%y %H:%M:%S")
    merged_df["date_time"] = merged_df["date_time"].apply(
        lambda x: x if x.year <= 2022 else x - pd.DateOffset(years=100)
    )
    merged_df["date"] = merged_df["date_time"].dt.date
    merged_df["time"] = merged_df["date_time"].dt.time

    new_regimes = {}
    new_measures = []
    indexes = set()

    # Loop through each row in the DataFrame
    for index, row in merged_df.iterrows():
        well = wells_dict.get(row["ScvID"])
        if (row["Uroven"] or row["Temperatura"]) and well:
            checker = (well, row["date"])
            if checker not in indexes:
                regime = WellsRegime(well=well, date=row["date"], extra=data_source, last_user=user)
                indexes.add(checker)
                new_regimes[checker] = regime
            new_measures.append(
                (
                    row["Uroven"],
                    row["Temperatura"],
                    row["time"],
                    new_regimes[checker],
                )
            )

    WellsRegime.objects.bulk_create(list(new_regimes.values()), batch_size)
    newly_created_regimes = {
        (
            instance.well,
            instance.date,
        ): instance
        for instance in WellsRegime.objects.only("well", "date")
    }
    et = time.time()
    print(f"Regime: {et - st}")

    wells_watmeasure_list = []
    wells_tempmeasure_list = []
    content_type_regime = ContentType.objects.get_for_model(WellsRegime)
    for i, (uroven, tmpr, time_p, regime) in enumerate(new_measures):
        measure_inst = newly_created_regimes.get(
            (
                regime.well,
                regime.date,
            )
        )
        if measure_inst:
            if uroven:
                wat_inst = WellsWaterDepth(
                    water_depth=uroven,
                    extra=data_source,
                    time_measure=time_p,
                    content_type=content_type_regime,
                    object_id=regime.id,
                    last_user=user,
                )
                wells_watmeasure_list.append(wat_inst)
            if tmpr:
                tmpr_inst = WellsTemperature(
                    temperature=tmpr,
                    extra=data_source,
                    time_measure=time_p,
                    content_type=content_type_regime,
                    object_id=regime.id,
                    last_user=user,
                )
                wells_tempmeasure_list.append(tmpr_inst)

    WellsWaterDepth.objects.bulk_create(wells_watmeasure_list, batch_size)
    WellsTemperature.objects.bulk_create(wells_tempmeasure_list, batch_size)
    print("wells_regime")

    wells_sample = pd.read_csv("./scripts/sources/data/ChemProba.csv")
    wells_prot = pd.read_csv("./scripts/sources/data/ChemAnalysis.csv")
    wells_comp = pd.read_csv("./scripts/sources/data/ChemAnalysisComponent.csv")
    wells_chem = wells_sample.join(wells_prot.set_index("ProbaNumber"), on="ProbaNumber")
    wells_chem = wells_comp.join(wells_chem.set_index("AnalysisNumber"), on="AnalysisNumber")
    wells_chem = wells_chem[~wells_chem["DateOtbor"].isna()]
    wells_chem = wells_chem.drop_duplicates(subset=["IDPN", "DateOtbor", "ProbaNumber", "ComponentCode"], keep="last")
    wells_chem["date_time"] = pd.to_datetime(wells_chem["DateOtbor"], format="%m/%d/%y %H:%M:%S")
    wells_chem["date_time"] = wells_chem["date_time"].apply(
        lambda x: x if x.year <= 2022 else x - pd.DateOffset(years=100)
    )
    wells_chem["date"] = wells_chem["date_time"].dt.date
    samples = {}
    chem_values = []
    indexes = set()
    for index, row in wells_chem.iterrows():
        well = wells_dict.get(row["IDPN"])
        if well and row["ProbaNumber"]:
            checker = (
                well,
                row["date"],
                row["ProbaNumber"],
            )
            if checker not in indexes:
                sample = WellsSample(
                    well=well, date=row["date"], name=row["ProbaNumber"], extra=data_source, last_user=user
                )
                indexes.add(checker)
                samples[checker] = sample
            chem_values.append((int(row["ComponentCode"]), row["ComponentValue"], samples[checker]))
    WellsSample.objects.bulk_create(list(samples.values()), batch_size)

    newly_created_chem = {
        (
            instance.well,
            instance.date,
            instance.name,
        ): instance
        for instance in WellsSample.objects.filter(
            date__in=[r.date for r in samples.values()], well__in=[r.well for r in samples.values()]
        )
    }

    content_type_sample = ContentType.objects.get_for_model(WellsSample)
    chem_codes_dict = {chem.chem_id: chem for chem in ChemCodes.objects.only("chem_id")}
    wells_chem_list = []
    for i, (code, value, sample) in enumerate(chem_values):
        sample_inst = newly_created_chem.get((sample.well, sample.date, str(sample.name)))
        if sample_inst:
            chem_instance = WellsChem(
                parameter=chem_codes_dict[code],
                chem_value=value,
                extra=data_source,
                last_user=user,
                content_type=content_type_sample,
                object_id=sample_inst.id,
            )
            wells_chem_list.append(chem_instance)
    WellsChem.objects.bulk_create(wells_chem_list, batch_size)
    print("wells_chem")

    wells_construction = pd.read_csv("./scripts/sources/data/ScvDocumantation.csv")
    wells_construction = wells_construction[~wells_construction["TypeOfFiltrID"].isna()]
    wells_construction = wells_construction[wells_construction["Date"] != "01/00/00 00:00:00"]
    wells_construction["date_time"] = pd.to_datetime(wells_construction["Date"], format="%m/%d/%y %H:%M:%S")
    wells_construction["date_time"] = wells_construction["date_time"].apply(
        lambda x: x if x.year <= 2022 else x - pd.DateOffset(years=100)
    )
    wells_construction["date"] = wells_construction["date_time"].dt.date
    construction_dict = {
        cstr.extra["old_code"]: cstr
        for cstr in DictEntities.objects.only("name", "extra").filter(entity__name="тип конструкции скважины")
    }
    cstr_list = []
    for index, row in wells_construction.iterrows():
        well = wells_dict.get(row["ScvID"])
        if well:
            cstr_instance = WellsConstruction(
                well=well,
                date=row["date"],
                depth_from=row["DeepFrom"],
                depth_till=row["DeepTo"],
                diameter=row["DiametrTrub"],
                construction_type=construction_dict[row["TypeOfFiltrID"]],
                extra=data_source,
                last_user=user,
            )
            cstr_list.append(cstr_instance)
    WellsConstruction.objects.bulk_create(cstr_list, batch_size)
    print("wells_construction")

    balance = pd.read_csv("./scripts/sources/data/RGWLayer.csv")
    balance = balance[~balance["nazg"].isna()].replace(np.nan, None)
    content_type_balances = ContentType.objects.get_for_model(Fields)
    fields_dict = {inst.extra["name_gwk"]: inst for inst in Fields.objects.only("id", "extra")}
    aquifer_dict = {inst.aquifer_id: inst for inst in AquiferCodes.objects.only("aquifer_id")}
    gw_type = {
        inst.extra["old_code"]: inst
        for inst in DictEntities.objects.only("name", "extra").filter(entity__name="тип подземных вод")
    }
    balance_list = []
    for index, row in balance.iterrows():
        field = fields_dict.get(row["kmpv"])
        if field:
            balance_inst = Balance(
                aquifer=aquifer_dict[row["kgor"]],
                typo=gw_type[row["nazg"]],
                a=row["zapA"] if row["zapA"] else 0,
                b=row["zapB"] if row["zapB"] else 0,
                c1=row["zapC1"] if row["zapC1"] else 0,
                c2=row["zapC2"] if row["zapC2"] else 0,
                extra=data_source,
                last_user=user,
                object_id=field.id,
                content_type=content_type_balances,
            )
            balance_list.append(balance_inst)
    Balance.objects.bulk_create(balance_list, batch_size)
    print("balances")

    wells_drill = pd.read_csv("./scripts/sources/data/ScvObor.csv")
    wells_catalog = pd.read_csv("./scripts/sources/data/ScvCatalog.csv")
    wells_drill["BurenieYear_Start"] = wells_drill["Date"]
    drilled_data = pd.merge(wells_drill, wells_catalog, on=["ScvID", "BurenieYear_Start"], how="left")
    drilled_data = drilled_data[~drilled_data["BurenieYear_Finish"].isna()]

    drilled_data = drilled_data[drilled_data["BurenieYear_Finish"] != "01/00/00 00:00:00"]
    drilled_data["date_time_start"] = pd.to_datetime(drilled_data["BurenieYear_Start"], format="%m/%d/%y %H:%M:%S")
    drilled_data["date_time_start"] = drilled_data["date_time_start"].apply(
        lambda x: x if x.year <= 2022 else x - pd.DateOffset(years=100)
    )
    drilled_data["date_start"] = drilled_data["date_time_start"].dt.date
    drilled_data["date_time_end"] = pd.to_datetime(drilled_data["BurenieYear_Finish"], format="%m/%d/%y %H:%M:%S")
    drilled_data["date_time_end"] = drilled_data["date_time_end"].apply(
        lambda x: x if x.year <= 2022 else x - pd.DateOffset(years=100)
    )
    drilled_data["date_end"] = drilled_data["date_time_end"].dt.date
    drilled_data = drilled_data.replace(np.nan, None)
    drl_list = []
    depth_cond = []
    for index, row in drilled_data.iterrows():
        well = wells_dict.get(row["ScvID"])
        if well:
            drl_data = WellsDrilledData(
                well=well,
                date_start=row["date_start"],
                date_end=row["date_end"],
                organization=row["BurOrgID"],
                last_user=user,
                extra=data_source,
            )
            drl_list.append(drl_data)
            depth_cond.append((row["ScvDeep"], row["TechSost"], drl_data))
    WellsDrilledData.objects.bulk_create(drl_list, batch_size)

    content_type_drill = ContentType.objects.get_for_model(WellsDrilledData)
    condition_type = {
        inst.extra["old_code"]: inst
        for inst in DictEntities.objects.only("name", "extra").filter(entity__name="тех.состояние скважины")
    }
    depth_list = []
    cond_list = []
    drl_instances = {
        (
            instance.well,
            instance.date_start,
        ): instance
        for instance in WellsDrilledData.objects.all()
    }
    for depth, condition, data in depth_cond:
        instance = drl_instances.get(
            (
                data.well,
                data.date_start,
            )
        )
        if instance:
            if depth:
                dpth = WellsDepth(
                    depth=depth,
                    content_type=content_type_drill,
                    object_id=instance.id,
                    extra=data_source,
                    last_user=user,
                )
                depth_list.append(dpth)
            if condition:
                cnd = WellsCondition(
                    condition=condition_type[condition],
                    content_type=content_type_drill,
                    object_id=instance.id,
                    extra=data_source,
                    last_user=user,
                )
                cond_list.append(cnd)
    WellsDepth.objects.bulk_create(depth_list, batch_size)
    WellsCondition.objects.bulk_create(cond_list, batch_size)
    print("wells_drilled_data")

    license_df = pd.read_csv("./scripts/sources/data/T1_202307221507.csv")
    license_df = license_df[~license_df["F04"].isna()]
    license_df["date_time_start"] = pd.to_datetime(license_df["F02"], format="%Y-%m-%d %H:%M:%S.%f")
    license_df["date_time_end"] = pd.to_datetime(license_df["F17"], format="%Y-%m-%d %H:%M:%S.%f")
    license_df["date_start"] = license_df["date_time_start"].dt.date
    license_df["date_end"] = license_df["date_time_end"].dt.date
    for index, row in license_df.iterrows():
        name = f"{row['F03']}{str(int(row['F04'])).zfill(5)}{row['F05']}"
        extra = {"name_gwk": row["IDL"]}
        extra.update(data_source)
        org = DictDocOrganizations.objects.filter(name=row["F18"]).first()
        if not org:
            org = DictDocOrganizations(name=row["F18"])
            org.save()
        License(
            name=name,
            date_start=row["date_start"],
            date_end=row["date_end"],
            comments=row["F59"],
            gw_purpose=row["F42"],
            department=org,
            extra=extra,
        ).save()
    print("license")

    license_dict = {instance.extra["name_gwk"]: instance for instance in License.objects.only("id", "extra")}
    license_wells = pd.read_csv("./scripts/sources/data/_Scv_License__202307221507.csv")
    for index, row in license_wells.iterrows():
        licenses = license_dict.get(row["IDL"])
        well = wells_dict.get(row["ScvID"])
        if licenses and well:
            LicenseToWells(well=well, license=licenses).save()
    print("license_wells")

    license_df["code"] = license_df["F85"]
    wateruser_df = pd.read_csv("./scripts/sources/dictionaries/_00007__202305050201.csv")
    wateruser_df = pd.merge(wateruser_df, license_df, on="code", how="left")
    wateruser_df = wateruser_df.drop_duplicates(subset="article", keep="first").replace(np.nan, None)
    wateruser_list = []
    for index, row in wateruser_df.iterrows():
        extra = {"name_gwk": row["code"]}
        extra.update(data_source)
        wateruser_list.append(WaterUsers(name=row["article"], position=row["F14"], extra=extra, last_user=user))
    WaterUsers.objects.bulk_create(wateruser_list, batch_size)

    water_user_dict = {instance.extra["name_gwk"]: instance for instance in WaterUsers.objects.only("extra")}
    indexes = set()
    changes_users = []
    for index, row in license_df.iterrows():
        watusr = water_user_dict.get(row["code"])
        if watusr:
            checker = (
                watusr,
                row["date_start"],
            )
            if checker not in indexes:
                changes_users.append(
                    WaterUsersChange(
                        water_user=watusr,
                        date=row["date_start"],
                        license=license_dict[row["IDL"]],
                        last_user=user,
                        extra=data_source,
                    )
                )
                indexes.add(checker)
    WaterUsersChange.objects.bulk_create(changes_users, batch_size)
    print("water_users")

    pump = pd.read_csv("./scripts/sources/data/ScvNasos.csv")
    pump = pump["NasosMarkID"].unique()
    pump_type = DictEntities.objects.get(entity__name="тип оборудования", name="насос")
    for p in pump:
        DictEquipment(typo=pump_type, brand=p).save()

    efw_df = pd.read_csv("./scripts/sources/data/ScvObsled.csv")
    efw_df = efw_df[~efw_df["OpitType"].isna()]
    efw_df = efw_df[efw_df["Date"] != "01/00/00 00:00:00"]
    efw_df["date_time_start"] = pd.to_datetime(efw_df["Date"], format="%m/%d/%y %H:%M:%S")
    efw_df["date_time_start"] = efw_df["date_time_start"].apply(
        lambda x: x if x.year <= 2022 else x - pd.DateOffset(years=100)
    )
    efw_df["date"] = efw_df["date_time_start"].dt.date
    efw_df["time"] = efw_df["date_time_start"].dt.time
    efw_df = efw_df.replace(np.nan, None)
    content_type_stat = ContentType.objects.get_for_model(WellsEfw)
    content_type_dyn = ContentType.objects.get_for_model(WellsDepression)
    efw_type = {
        instance.extra["old_code"]: instance
        for instance in DictEntities.objects.only("extra").filter(entity__name="тип офр")
    }
    for index, row in efw_df.iterrows():
        well = wells_dict.get(row["ScvID"])
        if well:
            efw = WellsEfw(
                well=well,
                date=timezone.make_aware(row["date_time_start"]),
                type_efw=efw_type.get(row["OpitType"]),
                pump_time="01:00:00",
                extra=data_source,
            )
            efw.save()
            if row["StatUr"]:
                WellsWaterDepth(
                    object_id=efw.id,
                    time_measure=row["time"],
                    water_depth=row["StatUr"],
                    content_type=content_type_stat,
                    type_level=True,
                    extra=data_source,
                ).save()
            depression = WellsDepression(efw_id=efw)
            depression.save()
            if row["DynUr"]:
                WellsWaterDepth(
                    object_id=depression.id,
                    water_depth=row["DynUr"],
                    content_type=content_type_dyn,
                    time_measure="01:00:00",
                    type_level=False,
                    extra=data_source,
                ).save()
            if row["Debit"]:
                WellsRate(
                    object_id=depression.id,
                    rate=row["Debit"],
                    content_type=content_type_dyn,
                    time_measure="01:00:00",
                    extra=data_source,
                ).save()
    print("wells_efw")
    et = time.time()
    print(f"End: {et - st}")
