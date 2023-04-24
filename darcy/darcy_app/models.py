import uuid
from django.utils import timezone
from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords


def user_directory_path(instance, filename):
	return 'doc_{0}/{1}'.format(instance.doc.pk, filename)

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
    author = models.CharField(editable=False, null=True, blank=True, default='ufo')
    last_user = models.ForeignKey(get_user_model(), editable=False, on_delete=models.CASCADE)
    remote_addr = models.GenericIPAddressField(editable=False, null=True, blank=True,)
    extra = models.JSONField(editable=False, blank=True, null=True)
    uuid = models.UUIDField(editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
            self.author = 'ufo'

        self.modified = timezone.now()
        self.last_user = get_user_model().objects.first()
        super(BaseModel, self).save(*args, **kwargs)


class Entities(BaseModel):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Сущность'
        verbose_name_plural = 'Сущности'
        db_table = 'entities'

    def __str__(self):
        return self.name


class DictEntities(BaseModel):
    name = models.CharField(max_length=250)
    entity = models.ForeignKey('Entities', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Словарь сущностей'
        verbose_name_plural = 'Словарь сущностей'
        db_table = 'dict_entities'
        unique_together = (('name', 'entity'),)

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
    """
    name = models.CharField(max_length=1200, verbose_name='Название документа')
    typo = models.ForeignKey(
            'DictEntities', models.DO_NOTHING, related_name='doc_type',
            verbose_name='Тип документа'
            )
    source = models.ForeignKey(
            'DictEntities', models.DO_NOTHING, db_column='doc_source',
            related_name='doc_source', verbose_name='Источник поступления',
            blank=True, null=True
            )
    org_executor = models.ForeignKey(
            'DictEntities', models.DO_NOTHING, db_column='org_executor',
            related_name='org_executor', verbose_name='Организация-исполнитель',
            blank=True, null=True
            )
    org_customer = models.ForeignKey(
            'DictEntities', models.DO_NOTHING, db_column='org_customer',
            related_name='org_customer', verbose_name='Организация-заказчик',
            blank=True, null=True
            )
    creation_date = models.DateField(
            blank=True, null=True,
            verbose_name='Дата создания документа'
            )
    creation_place = models.CharField(
            max_length=200, blank=True, null=True,
            verbose_name='Место создания документа'
            )
    links = models.ManyToManyField('self', symmetrical=False, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='documents_history')

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документация'
        db_table = 'documents'
        unique_together = (('content_type', 'object_id'),)

    def __str__(self):
        return self.name


class DocumentsPath(BaseModel):
    doc = models.ForeignKey('Documents', on_delete=models.CASCADE)
    path = models.FileField(upload_to=user_directory_path)
    history = HistoricalRecords(table_name='documents_path_history')

    class Meta:
        verbose_name = 'Путь к документу'
        verbose_name_plural = 'Пути к документам'
        db_table = 'documents_path'
 

class AquiferCodes(models.Model):
    aquifer_name = models.CharField(max_length=150, verbose_name='Название гидрогеологического подразделения')
    aquifer_index = models.CharField(unique=True, max_length=50, verbose_name='Индекс геологического подразделения')

    class Meta:
        verbose_name = 'Гидрогеологическое подразделение'
        verbose_name_plural = 'Словарь гидрогеологических подразделений'
        db_table = 'aquifer_codes'

    def __str__(self):
        return self.aquifer_name


class Wells(BaseModel):
    """
    Модель скважин, содержащая информацию о скважинах,
    такую как их номер скважины (ГВК), название,
    тип, абсолютная отметка, водоносный горизонт, название водозабора и
    геометрическое представление.
    """
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Название скважины')
    typo = models.ForeignKey(
            'DictEntities', models.DO_NOTHING,
            related_name='well_type', verbose_name='Тип скважины'
            )
    head = models.DecimalField(
            max_digits=6, decimal_places=2, blank=True, null=True,
            verbose_name='Абсолютная отметка, м',
            help_text='до двух знаков после запятой'
            )
    aquifer = models.ForeignKey(
            'AquiferCodes', models.DO_NOTHING, blank=True, null=True,
            verbose_name='Водоносный горизонт'
            )
    intake = models.ForeignKey(
            'Intakes', models.DO_NOTHING, blank=True, null=True,
            verbose_name='Название водозабора')
    geom = models.PointField(
            srid=4326, blank=True, null=True, 
            verbose_name='Геометрия',
            help_text='WGS84',
            )
    docs = GenericRelation('Documents')
    history = HistoricalRecords(table_name='wells_history')

    class Meta:
        verbose_name = 'Скважина'
        verbose_name_plural = 'Скважины'
        db_table = 'wells'

    def __str__(self):
        return self.name


class Intakes(BaseModel):
    """
     Модель для представления водозаборов. Содержит
     название и геометрию водозабора.
    """
    intake_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Название водозабора')
    geom = models.MultiPolygonField(
            srid=4326, blank=True, null=True,
            verbose_name='Геометрия',
            help_text='WGS84'
            )
    history = HistoricalRecords(table_name='intakes_history')

    class Meta:
        verbose_name = 'Водозабор'
        verbose_name_plural = 'Водозаборы'
        db_table = 'intakes'

    def __str__(self):
        return self.intake_name


class WellsRegime(BaseModel):
    """
    Модель для представления режимных наблюдений скважин. Содержит внешний
    ключ для скважины, дату замера, связь с документацией и обобщенные связи
    с глубиной УГВ и дебитом (или другими возможными режимными измерениями).
    """
    well = models.ForeignKey('Wells', models.CASCADE, verbose_name='Номер скважины')
    date = models.DateTimeField(verbose_name='Дата и время замера')
    doc = models.ForeignKey('Documents', models.CASCADE, blank=True, null=True)
    waterdepths = GenericRelation('WellsWaterDepth')
    rates = GenericRelation('WellsRate')
    history = HistoricalRecords(table_name='wells_regime_history')

    class Meta:
        verbose_name = 'Режимное наблюдение'
        verbose_name_plural = 'Режимные наблюдения'
        db_table = 'wells_regime'
        unique_together = (('well', 'date'),)

    def __str__(self):
        return(f'{self.well} {self.date}')


class WellsWaterDepth(BaseModel):
    """
    Модель для представления замеров глубины УГВ. Содержит значения
    глубины УГВ и обобщенные связи с другими возможными моделями.
    """
    water_depth = models.DecimalField(
            max_digits=6, decimal_places=2, verbose_name='Глубина УГВ, м',
            help_text='до двух знаков после запятой'
            )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='wells_water_depth_history')

    class Meta:
        verbose_name = 'Замер УГВ'
        verbose_name_plural = 'Замеры УГВ'
        db_table = 'wells_water_depth'
        unique_together = (('object_id', 'content_type'),)


class WellsRate(BaseModel):
    """
    Модель для представления замеров дебита скважин. Содержит значения дебита
    и обобщенные связи с другими возможными моделями.
    """
    rate = models.DecimalField(
            max_digits=7, decimal_places=3, verbose_name='Дебит л/с',
            help_text='до трех знаков после запятой'
            )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='wells_rate_history')

    class Meta:
        verbose_name = 'Замер дебита'
        verbose_name_plural = 'Замеры дебита'

        db_table = 'wells_rate'
        unique_together = (('object_id', 'content_type'),)


class WellsDepth(BaseModel):
    """
    Модель для представления замеров глубины скважин. Содержит значения глубины
    и обобщенные связи с другими возможными моделями.
    """
    depth = models.DecimalField(
            max_digits=6, decimal_places=2, verbose_name='Глубина скважины, м',
            help_text='до двух знаков после запятой'
            )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='wells_depth_history')

    class Meta:
        verbose_name = 'Глубина скважины'
        verbose_name_plural = 'Глубина скважин'
        db_table = 'wells_depth'
        unique_together = (('object_id', 'content_type'),)


class WellsAquifers(BaseModel):
    """
    Модель гидрогеологического описание скважин.
    Содержит информацию о водоносных горизонтах и глубине
    подошвы горизонта.
    Через внешний ключ с Documents осуществляется связь гидрогеологического
    описания скважины с документацией, в которой она представлена
    (к примеру: паспорт скважины, геол.описание скажины, учетная карточка скважины и т.д.)
    """
    well = models.ForeignKey('Wells', models.CASCADE, verbose_name='Номер скважины')
    aquifer = models.ForeignKey('AquiferCodes', models.DO_NOTHING, verbose_name='Водоносный горизонт')
    bot_elev = models.DecimalField(
            max_digits=6, decimal_places=2,
            verbose_name='Глубина подошвы горизонта, м',
            help_text='до двух знаков после запятой'
            )
    doc = models.ForeignKey('Documents', models.CASCADE, blank=True, null=True)
    history = HistoricalRecords(table_name='wells_aquifers_history')

    class Meta:
        verbose_name = 'Гидрогеологическая колонка'
        verbose_name_plural = 'Гидрогеологические колонки'
        db_table = 'wells_aquifers'
        unique_together = (('well', 'aquifer'),)


class WellsEfw(BaseModel):
    """
    Модель опытно-фильтрационных работ (ОФР) в скважинах.
    Содержит информацию о типе опыта, водоподъемном оборудовании,
    глубине загрузки оборудования, продолжительности опыта и дебите.
    Через внешний ключ с Documents осуществляется связь ОФР с 
    актами ОФР и другой документацией, связанной с проведением ОФР
    """
    well = models.ForeignKey('Wells', models.CASCADE, verbose_name='Номер скважины')
    date = models.DateTimeField(verbose_name='Дата и время опыта')
    type_efw = models.ForeignKey(
            'DictEntities', models.DO_NOTHING, db_column='type_efw',
            related_name='type_efw', verbose_name='Тип опыта'
            )
    # pump_type: погружной насос, аэрлифт и проч...
    pump_type = models.ForeignKey(
            'DictEntities', models.DO_NOTHING, db_column='pump_type',
            related_name='pump_type',
            verbose_name='Тип водоподъемного оборудования'
            )
    pump_depth = models.DecimalField(
            max_digits=6, decimal_places=2,
            verbose_name='Глубина загрузки водоподъемного оборудования, м',
            help_text='до двух знаков после запятой',
            blank=True, null=True
            )
    pump_time = models.TimeField(verbose_name='Продолжительность опыта')
    rates = GenericRelation('WellsRate')
    doc = models.ForeignKey('Documents', models.CASCADE, blank=True, null=True)
    waterdepths = GenericRelation('WellsWaterDepth')
    history = HistoricalRecords(table_name='wells_efw_history')

    class Meta:
        verbose_name = 'ОФР'
        verbose_name_plural = 'Опытно-фильтрационные работы'
        db_table = 'wells_efw'
        unique_together = (('well', 'date'),)

    def __str__(self):
        return f'{self.well}-{self.date} {self.type_efw}'


class WellsDepression(BaseModel):
    """
    Модель журнала опытно-фильтрационных работ (ОФР).
    Содержит информацию о времени замера динамического уровня и
    значениях динамического уровня.
    """
    efw_id = models.ForeignKey('WellsEfw', models.CASCADE)
    time_measure = models.TimeField(
            verbose_name='Время замера',
            help_text='время от начала опыта'
            )
    waterdepths = GenericRelation('WellsWaterDepth')
    history = HistoricalRecords(table_name='wells_depression_history')

    class Meta:
        verbose_name = 'Журнал ОФР'
        verbose_name_plural = 'Журнал ОФР'
        db_table = 'wells_depression'
        unique_together = (('efw_id', 'time_measure'),)


class WellsSample(BaseModel):
    """
    Проба
    Содержит информацию о дате отбора пробы и номере пробы.
    Через внешний ключ с Documents осуществляется связь опробований скважин
    с химическими протоколами (исследованиями этой пробы)
    """
    well = models.ForeignKey('Wells', models.CASCADE, verbose_name='Номер скважины')
    date = models.DateField(verbose_name='Дата опробования')
    name = models.CharField(max_length=150, verbose_name='Номер пробы')
    doc = models.ForeignKey('Documents', models.CASCADE, blank=True, null=True)
    chemvalues = GenericRelation('WellsChem')
    history = HistoricalRecords(table_name='wells_sample_history')

    class Meta:
        verbose_name = 'Хим. опробование'
        verbose_name_plural = 'Хим. опробования'
        db_table = 'wells_sample'
        unique_together = (('well', 'date'),)

    def __str__(self):
        return f'{self.well}-{self.date} {self.name}'


class ChemCodes(models.Model):
    """
    Словарь показателей химического состава подземных вод
    """
    chem_name = models.CharField(unique=True, max_length=100, verbose_name='Наименование показателя')
    chem_formula = models.CharField(max_length=25, blank=True, null=True, verbose_name='Химическая формула показателя')
    chem_pdk = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, verbose_name='ПДК')
    chem_measure = models.CharField(max_length=25, blank=True, null=True, verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Показатель хим. состава'
        verbose_name_plural = 'Словарь показателей хим. состава'
        db_table = 'chem_codes'

    def __str__(self):
        return self.chem_name


class WellsChem(BaseModel):
    """
    Сведения о хим. показателях пробы, полученных в результате ее анализа
    """
    parameter = models.ForeignKey(
            'ChemCodes', models.DO_NOTHING, db_column='parameter',
            related_name='parameter', verbose_name='Хим. показатель'
            )
    chem_value = models.DecimalField(
            max_digits=10, decimal_places=5, blank=True, null=True,
            verbose_name='Значение показателя',
            help_text='до пяти знаков после запятой'
            )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='wells_chem_history')

    class Meta:
        verbose_name = 'Гидрогеохимия'
        verbose_name_plural = 'Гидрогеохимия'
        db_table = 'wells_chem'
        unique_together = (('parameter', 'object_id', 'content_type'),)


class Fields(BaseModel):
    """
    Участок месторождений подземных вод
    --------
    Полигон
    """
    field_name = models.CharField(max_length=100, verbose_name='Название УМПВ')
    geom = models.MultiPolygonField(
            srid=4326, blank=True, null=True,
            verbose_name='Геометрия',
            help_text='WGS84',
            )
    docs = GenericRelation('Documents')
    balances = GenericRelation('Balance')
    history = HistoricalRecords(table_name='fields_history')

    def __str__(self):
        return self.field_name

    class Meta:
        verbose_name = 'Участок месторождения ПВ'
        verbose_name_plural = 'Участки месторождения ПВ'
        db_table = 'fields'


class Balance(BaseModel):
    """
    Утвержденные запасы  на определенный
    водоносный горизонт и на определенный тип подземных вод (ПВ), м3
    """
    aquifer = models.ForeignKey('AquiferCodes', models.CASCADE, verbose_name='Водоносный горизонт')
    typo = models.ForeignKey(
            'DictEntities', models.CASCADE, verbose_name='Тип подземных вод',
            related_name='mineral'
            )
    a = models.DecimalField(
            max_digits=9, decimal_places=2, blank=True, null=True,
            verbose_name='A, м3'
            )
    b = models.DecimalField(
            max_digits=9, decimal_places=2, blank=True, null=True,
            verbose_name='B, м3'
            )
    c1 = models.DecimalField(
            max_digits=9, decimal_places=2, blank=True, null=True,
            verbose_name='C1, м3'
            )
    c2 = models.DecimalField(
            max_digits=9, decimal_places=2, blank=True, null=True,
            verbose_name='C2, м3'
            )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='fields_balance_history')

    class Meta:
        verbose_name = 'Утвержденные запасы'
        verbose_name_plural = 'Утвержденные запасы'
        db_table = 'fields_balance'


class Attachments(BaseModel):
    img = models.ImageField(upload_to='images/')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    history = HistoricalRecords(table_name='attachments_history')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        db_table = 'attachments'
