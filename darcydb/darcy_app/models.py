import base64
import io
import uuid

import boto3
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.utils.safestring import mark_safe
from pdf2image import convert_from_bytes
from simple_history.models import HistoricalRecords

from .storage_backends import YandexObjectStorage

__all__ = [
    "Entities",
    "DictEntities",
    "DictEquipment",
    "DictDocOrganizations",
    "Documents",
    "DocumentsPath",
    "AquiferCodes",
    "Wells",
    "WellsAquiferUsage",
    "Intakes",
    "WellsRegime",
    "WellsDrilledData",
    "WellsGeophysics",
    "WellsWaterDepth",
    "WellsRate",
    "WellsTemperature",
    "WellsDepth",
    "WellsCondition",
    "WellsLugHeight",
    "WellsAquifers",
    "WellsLithology",
    "WellsConstruction",
    "WellsEfw",
    "WellsDepression",
    "WellsSample",
    "ChemCodes",
    "WellsChem",
    "Fields",
    "Balance",
    "Attachments",
    "License",
    "LicenseToWells",
    "WaterUsers",
    "WaterUsersChange",
]


def user_directory_path(instance, filename):
    if instance.__dict__.get("doc_id"):
        return f"doc_{instance.doc_id}/{filename}"


class BaseModel(models.Model):
    """
    Абстрактный класс модели базы данных, который добавляет
    дополнительные поля и функциональность к другим моделям при наследовании.

        created: Дата и время создания объекта
        modified: Дата и время последнего изменения объекта
        author: Имя автора объекта
        last_user: Ссылка на последнего пользователя, который внес изменения в объект
        remote_addr: IP-адрес пользователя, который внес изменения в объект
        extra: JSON-поле для хранения дополнительной информации об объекте
        uuid: Уникальный идентификатор объекта, генерируется автоматически
    """

    created = models.DateTimeField(editable=False, null=True, blank=True)
    modified = models.DateTimeField(editable=False, null=True, blank=True)
    author = models.CharField(max_length=50, editable=False, null=True, blank=True, default="ufo")
    last_user = models.ForeignKey(get_user_model(), editable=False, on_delete=models.CASCADE)
    remote_addr = models.GenericIPAddressField(
        editable=False,
        null=True,
        blank=True,
    )
    extra = models.JSONField(editable=False, blank=True, null=True)
    uuid = models.UUIDField(editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
            self.author = "ufo"

        self.modified = timezone.now()
        self.last_user = get_user_model().objects.first()  # WTF ?
        super().save(*args, **kwargs)


class Entities(BaseModel):
    """
    Сущности
    """

    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Сущность"
        verbose_name_plural = "►Справочник Сущности"
        db_table = "entities"

    def __str__(self):
        return self.name


class DictEntities(BaseModel):
    """
    Справочник Сущностей
    fields = ["id", "name", "entity"]
    """

    name = models.CharField(max_length=250, verbose_name="Значение")
    entity = models.ForeignKey("Entities", on_delete=models.CASCADE, verbose_name="Справочник")

    class Meta:
        verbose_name = "Справочник сущностей"
        verbose_name_plural = "►Справочник Типы сущностей"
        db_table = "dict_entities"
        unique_together = (("name", "entity"),)

    def __str__(self):
        return self.name


class DictEquipment(BaseModel):
    """
    Справочник оборудования
    fields = ["id", "typo", "name", "brand"]
    """

    typo = models.ForeignKey("DictEntities", models.CASCADE, verbose_name="Тип оборудования")
    name = models.CharField(max_length=50, verbose_name="Название", blank=True, null=True)
    brand = models.CharField(max_length=50, verbose_name="Марка")

    class Meta:
        verbose_name = "Справочник оборудования"
        verbose_name_plural = "►Справочник обородувания"
        db_table = "dict_equipment"
        unique_together = (("brand", "typo"),)

    def __str__(self):
        return self.brand


class DictDocOrganizations(BaseModel):
    """
    Организации
    fields = ["id", "name"]
    """

    name = models.TextField(verbose_name="Название организации", unique=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "►Справочник организаций"
        db_table = "dict_doc_organization"

    def __str__(self):
        return self.name


class Documents(BaseModel):
    """
    Представляет собой документ с различными атрибутами,
    такими как название документа, источник, организации, ответственные за
    его выполнение и заказ, а также дата и место создания.
    Модель также предоставляет связь "многие ко многим" для связанных
    документов, а также универсальный внешний ключ для связи с различными
    типами связанных объектов.
    fields = ["id", "name", "typo", "source", "org_executor", "org_customer", "creation_date", "creation_place",
    "number_rgf", "number_tfgi", "authors", "links", "content_type", "object_id"]
    """

    name = models.CharField(max_length=1200, verbose_name="Название документа")
    typo = models.ForeignKey("DictEntities", models.DO_NOTHING, verbose_name="Тип документа")
    source = models.ForeignKey(
        "DictDocOrganizations",
        models.DO_NOTHING,
        db_column="source",
        related_name="doc_source",
        verbose_name="Источник поступления",
        blank=True,
        null=True,
    )
    org_executor = models.ForeignKey(
        "DictDocOrganizations",
        models.DO_NOTHING,
        db_column="org_executor",
        related_name="org_executor",
        verbose_name="Организация-исполнитель",
        blank=True,
        null=True,
    )
    org_customer = models.ForeignKey(
        "DictDocOrganizations",
        models.DO_NOTHING,
        db_column="org_customer",
        related_name="org_customer",
        verbose_name="Организация-заказчик",
        blank=True,
        null=True,
    )
    creation_date = models.DateField(blank=True, null=True, verbose_name="Дата создания документа")
    creation_place = models.CharField(max_length=200, blank=True, null=True, verbose_name="Место создания документа")
    number_rgf = models.CharField(max_length=10, blank=True, null=True, verbose_name="Инвентарный номер Росгеолфонда")
    number_tfgi = models.CharField(max_length=10, blank=True, null=True, verbose_name="Инвентарный номер ТФГИ")
    authors = models.TextField(
        blank=True, null=True, verbose_name="Авторы", help_text="Перечислите авторов через запятую"
    )
    links = models.ManyToManyField("self", symmetrical=False, blank=True, verbose_name="Связанные документы")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="documents_history")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "●Документы"
        db_table = "documents"
        unique_together = (
            (
                "name",
                "typo",
            ),
        )
        ordering = ("-creation_date",)

    def __str__(self):
        return self.name


class DocumentsPath(BaseModel):
    """
    Путь к документу
    fields = ["id", "doc", "path"]
    """

    doc = models.ForeignKey("Documents", on_delete=models.CASCADE)
    path = models.FileField(
        upload_to=user_directory_path,
        storage=YandexObjectStorage() if not settings.DEBUG else FileSystemStorage(location=settings.MEDIA_ROOT),
        verbose_name="Файл документа",
    )
    history = HistoricalRecords(table_name="documents_path_history")

    class Meta:
        verbose_name = "Путь к документу"
        verbose_name_plural = "Пути к документам"
        db_table = "documents_path"

    def __str__(self):
        return self.path.name

    # def save(self, *args, **kwargs):
    #     file = self.path
    #     self.path = ""
    #     super(DocumentsPath, self).save(*args, **kwargs)
    #     if file:
    #         file_path = self.generate_file_path(file.name)
    #         save_file_to_media_directory.delay(self.pk, file.read(), file_path)

    def delete(self, *args, **kwargs):
        if settings.DEBUG:
            storage, path = self.path.storage, self.path.path
            super().delete(*args, **kwargs)
            storage.delete(path)
        else:
            super().delete(*args, **kwargs)

    def generate_presigned_url(self):
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=YandexObjectStorage.endpoint_url,
            config=boto3.session.Config(signature_version=settings.AWS_S3_SIGNATURE_VERSION),
        )

        presigned_url = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": self.path.name}, ExpiresIn=3600
        )
        return presigned_url

    presigned_url = property(generate_presigned_url)


class AquiferCodes(models.Model):
    """
    Гидрогеологическое подразделение
    fields = ["aquifer_id", "aquifer_name", "aquifer_index"]
    """

    aquifer_id = models.IntegerField(primary_key=True)  # WTF?
    aquifer_name = models.CharField(
        max_length=150, unique=True, verbose_name="Название гидрогеологического подразделения"
    )
    aquifer_index = models.CharField(
        max_length=50, verbose_name="Индекс геологического подразделения", blank=True, null=True
    )

    class Meta:
        verbose_name = "Гидрогеологическое подразделение"
        verbose_name_plural = "►Справочник гидрогеологических подразделений"
        db_table = "aquifer_codes"

    def __str__(self):
        return f"{self.aquifer_name} ({self.aquifer_index})" if self.aquifer_index else self.aquifer_name


class Wells(BaseModel):
    """
    Модель скважин, содержащая информацию о скважинах,
    такую как их номер скважины (ГВК), название,
    тип, абсолютная отметка, водоносный горизонт, название водозабора и
    геометрическое представление.
    fields = ["id", "name", "typo", "head", "moved", "intake", "field", "geom"]
    """

    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Название скважины")
    typo = models.ForeignKey("DictEntities", models.DO_NOTHING, related_name="well_type", verbose_name="Тип скважины")
    head = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Абсолютная отметка устья, м",
        help_text="до двух знаков после запятой",
    )
    moved = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, verbose_name="Точность местоположения", blank=True, null=True
    )
    intake = models.ForeignKey("Intakes", models.DO_NOTHING, blank=True, null=True, verbose_name="Название водозабора")
    field = models.ForeignKey("Fields", models.DO_NOTHING, blank=True, null=True, verbose_name="Месторождение")
    geom = models.PointField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Геометрия",
        help_text="WGS84",
    )
    docs = GenericRelation("Documents")
    attachments = GenericRelation("Attachments")
    history = HistoricalRecords(table_name="wells_history")

    class Meta:
        verbose_name = "Скважина"
        verbose_name_plural = "Скважины"
        db_table = "wells"

    def __str__(self):
        try:
            try:
                name_gwk = self.extra.get("name_gwk")
            except Exception:
                name_gwk = ""
            if name_gwk:
                name_gwk = f"ГВК: {name_gwk}"
            return f"{str(self.uuid)[-5:]} {name_gwk}"
        except Exception:
            return f"well {self.pk}"


class WellsAquiferUsage(BaseModel):
    """
    Целевой водоносный горизонт скважины
    fields = ["id", "well", "aquifer"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Скважина")
    aquifer = models.ForeignKey(
        "AquiferCodes", models.DO_NOTHING, blank=True, null=True, verbose_name="Водоносный горизонт"
    )

    class Meta:
        verbose_name = "Целевой водоносный горизонт скважины"
        verbose_name_plural = "Целевые водоносные горизонты скважин"
        db_table = "wells_aquifer_usage"
        unique_together = (("well", "aquifer"),)


class Intakes(BaseModel):
    """
    Модель для представления водозаборов. Содержит
    название и геометрию водозабора.
    fields = ["id", "intake_name", "geom"]
    """

    intake_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Название водозабора")
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True, verbose_name="Геометрия", help_text="WGS84")
    history = HistoricalRecords(table_name="intakes_history")

    class Meta:
        verbose_name = "Водозабор"
        verbose_name_plural = "►Справочник Водозаборы"
        db_table = "intakes"
        # ordering = ("intake_name",)

    def __str__(self):
        return self.intake_name


class WellsRegime(BaseModel):
    """
    Модель для представления режимных наблюдений скважин. Содержит внешний
    ключ для скважины, дату замера, связь с документацией и обобщенные связи
    с глубиной УГВ и дебитом (или другими возможными режимными измерениями).
    fields = ["id", "well", "date", "doc"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    date = models.DateField(verbose_name="Дата замера")
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    waterdepths = GenericRelation("WellsWaterDepth")
    rates = GenericRelation("WellsRate")
    history = HistoricalRecords(table_name="wells_regime_history")

    class Meta:
        verbose_name = "Режимное наблюдение"
        verbose_name_plural = "Режимные наблюдения"
        db_table = "wells_regime"
        unique_together = (("well", "date"),)
        ordering = (
            "-date",
            "well",
        )

    def __str__(self):
        return f"{self.well} {self.date}"


class WellsDrilledData(BaseModel):
    """
    Модель для представления режимных наблюдений скважин. Содержит внешний
    ключ для скважины, дату замера, связь с документацией и обобщенные связи
    с глубиной УГВ и дебитом (или другими возможными режимными измерениями).
    fields = ["id", "well", "date_start", "date_end", "drill_type", "drill_rig", "organization", "doc"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    date_start = models.DateField(verbose_name="Дата начала бурения")
    date_end = models.DateField(verbose_name="Дата окончания бурения")
    drill_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Тип бурения")
    drill_rig = models.CharField(max_length=50, blank=True, null=True, verbose_name="Буровая установка")
    organization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Буровая организация")
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    waterdepths = GenericRelation("WellsWaterDepth")
    rates = GenericRelation("WellsRate")
    depths = GenericRelation("WellsDepth")
    conditions = GenericRelation("WellsCondition")
    history = HistoricalRecords(table_name="wells_drilled_data_history")

    class Meta:
        verbose_name = "Данные бурения"
        verbose_name_plural = "Данные бурения"
        db_table = "wells_drilled_data"
        unique_together = (("well", "date_end"),)
        ordering = (
            "-date_end",
            "well",
        )

    def __str__(self):
        return f"{self.well} {self.date_end}"


class WellsGeophysics(BaseModel):
    """
    Геофизические исследования
    fields = ["id", "well", "date", "organization", "researches", "conclusion", "doc"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    date = models.DateField(verbose_name="Дата производства работ")
    organization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Наименование организации")
    researches = models.TextField(verbose_name="Геофизические исследования")
    conclusion = models.TextField(verbose_name="Результаты исследований")
    depths = GenericRelation("WellsDepth")
    waterdepths = GenericRelation("WellsWaterDepth")
    attachments = GenericRelation("Attachments")
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    history = HistoricalRecords(table_name="wells_geophysics_history")

    class Meta:
        verbose_name = "Геофизические исследования"
        verbose_name_plural = "Геофизические исследования"
        db_table = "wells_geophysics"
        unique_together = (("well", "date"),)
        ordering = (
            "-date",
            "well",
        )

    def __str__(self):
        return f"{self.well} {self.date}"


class WellsWaterDepth(BaseModel):
    """
    Модель для представления замеров глубины УГВ. Содержит значения
    глубины УГВ и обобщенные связи с другими возможными моделями.
    fields = ["id", "type_level", "time_measure", "water_depth", "content_type", "object_id"]
    """

    type_level = models.BooleanField(verbose_name="Статический", blank=True, null=True, default=False)
    time_measure = models.DurationField(verbose_name="Время замера", blank=True, null=True)
    water_depth = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Глубина подземных вод, м",
        help_text="до двух знаков после запятой",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_water_depth_history")

    class Meta:
        verbose_name = "Замер уровня подземных вод"
        verbose_name_plural = "●Замеры уровня подземных вод"
        db_table = "wells_water_depth"
        unique_together = (("object_id", "content_type", "time_measure"),)

    def __str__(self):
        return ""


class WellsRate(BaseModel):
    """
    Модель для представления замеров дебита скважин. Содержит значения дебита
    и обобщенные связи с другими возможными моделями.
    fields = ["id", "time_measure", "rate", "content_type", "object_id"]
    """

    time_measure = models.DurationField(verbose_name="Время замера")
    rate = models.DecimalField(
        max_digits=7, decimal_places=3, verbose_name="Дебит л/с", help_text="до трех знаков после запятой"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_rate_history")

    class Meta:
        verbose_name = "Замер дебита"
        verbose_name_plural = "●Замеры дебита"
        db_table = "wells_rate"
        unique_together = (("object_id", "content_type", "time_measure"),)

    def __str__(self):
        return ""


class WellsTemperature(BaseModel):
    """
    Модель для представления замеров температур подземных вод. Содержит значения температур
    и обобщенные связи с другими возможными моделями.
    fields = ["id", "time_measure", "temperature", "content_type", "object_id"]
    """

    time_measure = models.DurationField(verbose_name="Время замера")
    temperature = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Температура, ℃", help_text="до двух знаков после запятой"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_temperature_history")

    class Meta:
        verbose_name = "Замер температуры подземных вод"
        verbose_name_plural = "●Замеры температуры подземных вод"
        db_table = "wells_temperature"
        unique_together = (("object_id", "content_type", "time_measure"),)

    def __str__(self):
        return ""


class WellsDepth(BaseModel):
    """
    Модель для представления замеров глубины скважин. Содержит значения глубины
    и обобщенные связи с другими возможными моделями.
    fields = ["id", "depth", "content_type", "object_id"]
    """

    depth = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Глубина скважины, м", help_text="до двух знаков после запятой"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_depth_history")

    class Meta:
        verbose_name = "Глубина скважины"
        verbose_name_plural = "●Глубина скважин"
        db_table = "wells_depth"
        unique_together = (("object_id", "content_type"),)

    def __str__(self):
        return ""


class WellsCondition(BaseModel):
    """
    Модель для представления замеров глубины скважин. Содержит значения глубины
    и обобщенные связи с другими возможными моделями.
    fields = ["id", "condition", "content_type", "object_id"]
    """

    condition = models.ForeignKey("DictEntities", on_delete=models.DO_NOTHING, verbose_name="Тех. состояние")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_condition_history")

    class Meta:
        verbose_name = "Тех.состояние скважины"
        verbose_name_plural = "●Тех.состояние скважин"
        db_table = "wells_condition"
        unique_together = (("object_id", "content_type"),)

    def __str__(self):
        return f"WellsCondition {self.pk}"


class WellsLugHeight(BaseModel):
    """
    Высота оголовка скважины
    fields = ["id", "lug_height", "content_type", "object_id"]
    """

    lug_height = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Высота оголовка, м", help_text="до двух знаков после запятой"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_lug_height_history")

    class Meta:
        verbose_name = "Высота оголовка скважины"
        verbose_name_plural = "●Высоты оголовков скважин"
        db_table = "wells_lug_height"
        unique_together = (("object_id", "content_type"),)

    def __str__(self):
        return f"Высота оголовка id: {self.pk}"


class WellsAquifers(BaseModel):
    """
    Модель гидрогеологического описание скважин.
    Содержит информацию о водоносных горизонтах и глубине
    подошвы горизонта.
    Через внешний ключ с Documents осуществляется связь гидрогеологического
    описания скважины с документацией, в которой она представлена
    (к примеру: паспорт скважины, геол.описание скажины, учетная карточка скважины и т.д.)
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    aquifer = models.ForeignKey("AquiferCodes", models.DO_NOTHING, verbose_name="Гидрогеологическое подразделение")
    bot_elev = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Глубина подошвы горизонта, м",
        help_text="до двух знаков после запятой",
    )
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    history = HistoricalRecords(table_name="wells_aquifers_history")

    class Meta:
        verbose_name = "Гидрогеологическая колонка"
        verbose_name_plural = "Гидрогеологические колонки"
        db_table = "wells_aquifers"
        unique_together = (("well", "aquifer"),)
        ordering = ("bot_elev",)

    def __str__(self):
        return ""


class WellsLithology(BaseModel):
    """
    Литологическая колонка
    fields = ["id", "well", "rock", "color", "composition", "structure", "mineral", "secondary_change",
    "cement", "fracture", "weathering", "caverns", "inclusions", "bot_elev", "doc"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    rock = models.ForeignKey("DictEntities", models.DO_NOTHING, verbose_name="Порода", related_name="rock")
    color = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, verbose_name="Цвет", related_name="color", blank=True, null=True
    )
    composition = models.ForeignKey(
        "DictEntities",
        models.DO_NOTHING,
        verbose_name="Гранулометрический состав",
        related_name="composition",
        blank=True,
        null=True,
    )
    structure = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, verbose_name="Структура", related_name="structure", blank=True, null=True
    )
    mineral = models.ForeignKey(
        "DictEntities",
        models.DO_NOTHING,
        verbose_name="Минеральный состав",
        related_name="mineral_cmspt",
        blank=True,
        null=True,
    )
    secondary_change = models.ForeignKey(
        "DictEntities",
        models.DO_NOTHING,
        verbose_name="Вторичные изменения",
        related_name="secondary_change",
        blank=True,
        null=True,
    )
    cement = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, verbose_name="Состав цемента", related_name="cement", blank=True, null=True
    )
    fracture = models.ForeignKey(
        "DictEntities",
        models.DO_NOTHING,
        verbose_name="Трещиноватость",
        related_name="fracture",
        blank=True,
        null=True,
    )
    weathering = models.ForeignKey(
        "DictEntities",
        models.DO_NOTHING,
        verbose_name="Степень выветрелости",
        related_name="weathering",
        blank=True,
        null=True,
    )
    caverns = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, verbose_name="Кавернозность", related_name="caverns", blank=True, null=True
    )
    inclusions = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, verbose_name="Включения", related_name="inclusions", blank=True, null=True
    )
    bot_elev = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Глубина до, м",
        help_text="до двух знаков после запятой",
    )
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    history = HistoricalRecords(table_name="wells_lithology_history")

    class Meta:
        verbose_name = "Литологическая колонка"
        verbose_name_plural = "Литологические колонки"
        db_table = "wells_lithology"
        unique_together = (("well", "rock", "bot_elev"),)
        ordering = ("bot_elev",)

    def __str__(self):
        return ""


class WellsConstruction(BaseModel):
    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    date = models.DateField(verbose_name="Дата установки", blank=True, null=True)
    construction_type = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, db_column="construction_type", verbose_name="Тип конструкции"
    )
    diameter = models.IntegerField(verbose_name="Диаметр")
    depth_from = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Глубина от, м")
    depth_till = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Глубина до, м")
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    history = HistoricalRecords(table_name="wells_construction_history")

    class Meta:
        verbose_name = "Конструкция скважины"
        verbose_name_plural = "Конструкция скважины"
        db_table = "wells_construction"
        unique_together = (("well", "date", "depth_from", "construction_type", "depth_till", "diameter"),)
        ordering = ("depth_from",)

    def __str__(self):
        return str(self.pk)


class WellsEfw(BaseModel):
    """
    Модель опытно-фильтрационных работ (ОФР) в скважинах.
    Содержит информацию о типе опыта, водоподъемном оборудовании,
    глубине загрузки оборудования, продолжительности опыта и дебите.
    Через внешний ключ с Documents осуществляется связь ОФР с
    актами ОФР и другой документацией, связанной с проведением ОФР
    fields = ["id", "well", "date", "type_efw", "pump_type", "level_meter", "pump_depth", "method_measure",
    "rate_measure", "pump_time", "vessel_capacity", "vessel_time", "doc"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    date = models.DateTimeField(verbose_name="Дата и время опыта")
    type_efw = models.ForeignKey(
        "DictEntities", models.DO_NOTHING, db_column="type_efw", related_name="type_efw", verbose_name="Тип опыта"
    )
    pump_type = models.ForeignKey(
        "DictEquipment",
        models.DO_NOTHING,
        db_column="pump_type",
        related_name="pump_type",
        verbose_name="Тип водоподъемного оборудования",
        blank=True,
        null=True,
    )
    level_meter = models.ForeignKey(
        "DictEquipment",
        models.DO_NOTHING,
        db_column="level_meter",
        related_name="level_meter",
        verbose_name="Уровнемер",
        blank=True,
        null=True,
    )
    pump_depth = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Глубина загрузки водоподъемного оборудования, м",
        help_text="до двух знаков после запятой",
        blank=True,
        null=True,
    )
    method_measure = models.ForeignKey(
        "DictEntities",
        models.DO_NOTHING,
        related_name="method_measure",
        verbose_name="Метод замера дебита",
        blank=True,
        null=True,
    )
    rate_measure = models.ForeignKey(
        "DictEquipment",
        models.DO_NOTHING,
        db_column="rate_measure",
        related_name="rate_measure",
        verbose_name="Расходомер",
        blank=True,
        null=True,
    )
    pump_time = models.DurationField(verbose_name="Продолжительность опыта")
    vessel_capacity = models.IntegerField(blank=True, null=True, verbose_name="Ёмкость мерного сосуда, м3")
    vessel_time = models.TimeField(blank=True, null=True, verbose_name="Время наполнения ёмкости, сек")
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    waterdepths = GenericRelation("WellsWaterDepth")
    lugs = GenericRelation("WellsLugHeight")
    history = HistoricalRecords(table_name="wells_efw_history")

    class Meta:
        verbose_name = "ОФР"
        verbose_name_plural = "Опытно-фильтрационные работы"
        db_table = "wells_efw"
        unique_together = (("well", "date"),)
        ordering = (
            "-date",
            "well",
        )

    def __str__(self):
        return f"{self.well}-{self.date} {self.type_efw}"


class WellsDepression(BaseModel):
    """
    Модель журнала опытно-фильтрационных работ (ОФР).
    Содержит информацию о времени замера динамического уровня и
    значениях динамического уровня.
    fields = ["id", "efw", "waterdepths", "rates"]
    """

    efw = models.ForeignKey("WellsEfw", models.CASCADE)
    waterdepths = GenericRelation("WellsWaterDepth")
    rates = GenericRelation("WellsRate")
    history = HistoricalRecords(table_name="wells_depression_history")

    class Meta:
        verbose_name = "Журнал ОФР"
        verbose_name_plural = "Журнал ОФР"
        db_table = "wells_depression"
        unique_together = (("efw",),)  # WTF ?

    def __str__(self):
        return str(self.pk)


class WellsSample(BaseModel):
    """
    Проба
    Содержит информацию о дате отбора пробы и номере пробы.
    Через внешний ключ с Documents осуществляется связь опробований скважин
    с химическими протоколами (исследованиями этой пробы)
    fields = ["id", "well", "date", "name", "doc"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    date = models.DateField(verbose_name="Дата опробования")
    name = models.CharField(max_length=150, verbose_name="Номер пробы")
    doc = models.ForeignKey("Documents", models.CASCADE, blank=True, null=True, verbose_name="Документ")
    chemvalues = GenericRelation("WellsChem")
    attachments = GenericRelation("Attachments")
    history = HistoricalRecords(table_name="wells_sample_history")

    class Meta:
        verbose_name = "Хим. опробование"
        verbose_name_plural = "Хим. опробования"
        db_table = "wells_sample"
        unique_together = (("well", "date", "name"),)
        ordering = (
            "-date",
            "well",
        )

    def __str__(self):
        return f"{self.well}-{self.date} {self.name}"


class ChemCodes(models.Model):
    """
    Справочник показателей химического состава подземных вод
    fields = ["chem_id", "chem_name", "chem_formula", "chem_pdk", "chem_measure"]
    """

    chem_id = models.IntegerField(primary_key=True)  # WTF?
    chem_name = models.CharField(unique=True, max_length=100, verbose_name="Наименование показателя")
    chem_formula = models.CharField(max_length=25, blank=True, null=True, verbose_name="Химическая формула показателя")
    chem_pdk = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, verbose_name="ПДК")
    chem_measure = models.CharField(max_length=25, blank=True, null=True, verbose_name="Единицы измерения")

    class Meta:
        verbose_name = "Показатель хим. состава"
        verbose_name_plural = "►Справочник показателей хим.состава"
        db_table = "chem_codes"
        ordering = ("chem_name",)

    def __str__(self):
        return self.chem_name


class WellsChem(BaseModel):
    """
    Сведения о хим. показателях пробы, полученных в результате ее анализа
    fields = ["id", "parameter", "chem_value", "content_type", "object_id"]
    """

    parameter = models.ForeignKey(
        "ChemCodes", models.DO_NOTHING, db_column="parameter", related_name="parameter", verbose_name="Хим. показатель"
    )
    chem_value = models.DecimalField(
        max_digits=15,
        decimal_places=5,
        blank=True,
        null=True,
        verbose_name="Значение показателя",
        help_text="до пяти знаков после запятой",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="wells_chem_history")

    class Meta:
        verbose_name = "Гидрогеохимия"
        verbose_name_plural = "●Гидрогеохимия"
        db_table = "wells_chem"
        unique_together = (("parameter", "object_id", "content_type"),)
        ordering = ("parameter__chem_name",)

    def __str__(self):
        return str(self.pk)


class Fields(BaseModel):
    """
    Месторождения подземных вод
    fields = ["id", "field_name", "geom"]
    --------
    Полигон
    """

    field_name = models.CharField(max_length=100, verbose_name="Название месторождения", unique=True)
    geom = models.MultiPolygonField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Геометрия",
        help_text="WGS84",
    )
    docs = GenericRelation("Documents")
    balances = GenericRelation("Balance")
    history = HistoricalRecords(table_name="fields_history")

    def __str__(self):
        return self.field_name

    class Meta:
        verbose_name = "Месторождение подземных вод"
        verbose_name_plural = "►Справочник Месторождения подземных вод"
        db_table = "fields"
        ordering = ("field_name",)


class Balance(BaseModel):
    """
    Утвержденные запасы  на определенный
    водоносный горизонт и на определенный тип подземных вод (ПВ), м3
    fields = ["id", "aquifer", "typo", "a", "b", "c1", "c2", "content_type", "object_id"]
    """

    aquifer = models.ForeignKey("AquiferCodes", models.CASCADE, verbose_name="Водоносный горизонт")
    typo = models.ForeignKey("DictEntities", models.CASCADE, verbose_name="Тип подземных вод", related_name="mineral")
    a = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, verbose_name="A, м3")
    b = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, verbose_name="B, м3")
    c1 = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, verbose_name="C1, м3")
    c2 = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, verbose_name="C2, м3")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="fields_balance_history")

    class Meta:
        verbose_name = "Утвержденные запасы"
        verbose_name_plural = "●Утвержденные запасы"
        db_table = "fields_balance"

    def __str__(self):
        return str(self.pk)


class Attachments(BaseModel):
    """
    Вложения
    ----------------
    fields = ["id", "img", "content_type", "object_id"]
    """

    img = models.FileField(
        upload_to="images/",
        storage=YandexObjectStorage() if not settings.DEBUG else FileSystemStorage(location=settings.MEDIA_ROOT),
        verbose_name="Вложение",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name="attachments_history")

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "●Вложения"
        db_table = "attachments"

    def image_tag(self):
        return mark_safe("<img src='/media/%s' width='150' height='150' />" % (self.img))

    def delete(self, *args, **kwargs):
        if settings.DEBUG:
            storage, path = (
                self.path.storage,
                self.path.path,  # ERROR? # E1101: Instance of 'Attachments' has no 'path' member (no-member)
            )
            super().delete(*args, **kwargs)
            storage.delete(path)
        else:
            super().delete(*args, **kwargs)

    def get_base64_image(self):
        image_content = []
        if self.img.name.endswith(".pdf"):
            images = convert_from_bytes(self.img.read())
            for image in images:
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                image_content.append(buffered.getvalue())
        else:
            if isinstance(self.img.storage, FileSystemStorage):
                # If the image is stored locally
                with open(self.img.path, "rb") as f:
                    image_content.append(f.read())
            else:
                # If the image is stored in Yandex Object Storage
                image_content.append(self.img.read())

        base64_images = [base64.b64encode(image).decode("utf-8") for image in image_content]
        return base64_images

    def __str__(self):
        return self.img.name

    image_tag.short_description = "Image"
    image_tag.allow_tags = True


class License(BaseModel):
    """
    Лицензии
    fields = ["id", "name", "department", "date_start", "date_end", "comments", "gw_purpose"]
    """

    name = models.CharField(unique=True, max_length=11, verbose_name="Номер лицензии")
    department = models.ForeignKey(
        "DictDocOrganizations", models.DO_NOTHING, db_column="department", verbose_name="Орган, выдавший лицензию"
    )
    date_start = models.DateField(blank=True, null=True, verbose_name="Дата выдачи лицензии")
    date_end = models.DateField(verbose_name="Дата окончания лицензии")
    comments = models.TextField(blank=True, null=True, verbose_name="Примечание")
    gw_purpose = models.TextField(verbose_name="Целевое назначение ПВ")
    docs = GenericRelation("Documents")
    history = HistoricalRecords(table_name="license_history")

    class Meta:
        verbose_name = "Лицензия"
        verbose_name_plural = "►Справочник Лицензии"
        db_table = "license"

    def __str__(self):
        return self.name


class LicenseToWells(BaseModel):
    """
    Связь скважины с лицензией
    fields = ["id", "well", "license"]
    """

    well = models.ForeignKey("Wells", models.CASCADE, verbose_name="Номер скважины")
    license = models.ForeignKey("License", models.CASCADE, verbose_name="Лицензия")
    history = HistoricalRecords(table_name="license_to_wells_history")

    class Meta:
        verbose_name = "Связь скважины с лицензией"
        verbose_name_plural = "Связи скважин с лицензиями"
        db_table = "license_to_wells"
        unique_together = (("well", "license"),)

    def __str__(self):
        return f"{self.pk}"


class WaterUsers(BaseModel):
    """
    Водопользователи
    fields = ["id", "name", "position"]
    """

    name = models.CharField(max_length=150, unique=True, verbose_name="Водопользователь")
    position = models.TextField(blank=True, null=True, verbose_name="Адрес")
    history = HistoricalRecords(table_name="water_users_history")

    class Meta:
        verbose_name = "Водопользователь"
        verbose_name_plural = "►Справочник Водопользователи"
        db_table = "water_users"

    def __str__(self):
        return self.name


class WaterUsersChange(BaseModel):
    """
    История водопользователя
    fields = ["id", "water_user", "date", "license"]
    """

    water_user = models.ForeignKey("WaterUsers", models.CASCADE, verbose_name="Водопользователь")
    date = models.DateField(verbose_name="Дата присвоения")
    license = models.ForeignKey("License", models.CASCADE, verbose_name="Номер лицензии")
    history = HistoricalRecords(table_name="water_users_change_history")

    class Meta:
        verbose_name = "История водопользователя"
        verbose_name_plural = "История водопользователя"
        db_table = "water_users_change"
        unique_together = (("water_user", "date"),)

    def __str__(self):
        return f"{self.water_user} - {self.date} - {self.license}"
