#from django.db import models
import os
import uuid as uuid_lib
from django.contrib.gis.db import models # gis django models
from django.utils import timezone
from django.db.models import JSONField
from django.db.models import F, Q, OuterRef, Subquery

from django.utils.html import mark_safe
try:
    from django.utils.translation import ugettext_lazy as _
except Exception:
    from django.utils.translation import gettext_lazy as _

from crum import get_current_request, get_current_user
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.gis.db.models.functions import AsGeoJSON # AsWKT new in Django3.1
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

__all__ = [
    'spr_change_reason',
    'spr_entity', 'spr_type', 'spr_vzu', 'spr_datasource', 'spr_pumps',
    'Poi', 'Observation', 'Foto', 'Fotos'
    ]


def validate_positive_float(value):
    if value < 0:
        raise ValidationError('это значение должно быть больше нуля!')


def validate_file_extension_pdf(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf',]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension. PDF only!')



class spr_change_reason(models.Model):
    class Meta:
        verbose_name = 'Справочник Причина изменений'
        verbose_name_plural = "•Справочник Причины изменений"

    name = models.CharField(verbose_name='причина', max_length=255, help_text='введите новую причину изменения строки')
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(spr_change_reason, self).save(*args, **kwargs)
        # search vector stuff
        spr_change_reason.objects.annotate(search_vector_name=SearchVector("name")).filter(
            id=self.id).update(search_vector=F("search_vector_name"))



class spr_pumps(models.Model):
    class Meta:
        verbose_name = 'Справочник Марка насоса'
        verbose_name_plural = "•Справочник Марки насосов"

    name = models.CharField(verbose_name='насос', max_length=255, help_text='насос')
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(spr_pumps, self).save(*args, **kwargs)
        # search vector stuff
        spr_pumps.objects.annotate(search_vector_name=SearchVector("name")).filter(
            id=self.id).update(search_vector=F("search_vector_name"))


class spr_datasource(models.Model):
    class Meta:
        verbose_name = 'Справочник Источник данных'
        verbose_name_plural = "•Справочник Источник данных"

    name = models.CharField(verbose_name='источник', max_length=255, help_text='указать источник данных')
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(spr_datasource, self).save(*args, **kwargs)
        # search vector stuff
        spr_datasource.objects.annotate(search_vector_name=SearchVector("name")).filter(
            id=self.id).update(search_vector=F("search_vector_name"))


class spr_entity(models.Model):
    class Meta:
        verbose_name = 'Справочник Сущность'
        verbose_name_plural = "•Справочник `сущности к типам`"

    name = models.CharField(verbose_name='сущность', max_length=255, help_text='сущность')
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(spr_entity, self).save(*args, **kwargs)
        # search vector stuff
        spr_entity.objects.annotate(search_vector_name=SearchVector("name")).filter(
            id=self.id).update(search_vector=F("search_vector_name"))


class spr_type(models.Model):
    class Meta:
        verbose_name = 'Справочник Тип'
        verbose_name_plural = "•Справочник Типы"

    name = models.CharField(verbose_name='тип', max_length=255, help_text='тип')
    apply_to = models.ForeignKey('spr_entity', verbose_name='для', help_text="выбрать сущность", on_delete=models.CASCADE)
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)


    def __str__(self):
        return str(self.name)
    

    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(spr_type, self).save(*args, **kwargs)
        # search vector stuff
        spr_type.objects.annotate(search_vector_name=SearchVector("name")).filter(
            id=self.id).update(search_vector=F("search_vector_name"))


class spr_vzu(models.Model):
    class Meta:
        verbose_name = 'Справочник Водозабор'
        verbose_name_plural = "•Справочник Водозаборы"
    
    name = models.CharField(verbose_name='водозабор', max_length=255, help_text='водозабор')
    #typo = models.ForeignKey('spr_type', verbose_name='тип водозабора',  on_delete=models.CASCADE)
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(spr_vzu, self).save(*args, **kwargs)
        # search vector stuff
        spr_vzu.objects.annotate(search_vector_name=SearchVector("name")).filter(
            id=self.id).update(search_vector=F("search_vector_name"))


class Fotos(models.Model):
    '''
    Фотографии
    '''
    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'фото'
    
    image = models.ImageField(_('фото'), upload_to = "foto")
    description = models.CharField(_('описание'), max_length=255, blank=True, null=True,  help_text='ввести краткое (255 символов) описание фотографии')
    # the required fields to enable a generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    #hidden fields
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    

    def __str__(self):
        return self.image.url        

    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.lastuser = user
        self.modified = timezone.now()
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(Fotos, self).save(*args, **kwargs)


class Foto(models.Model):
    '''
    Фотографии
    '''
    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'фото'

    image = models.ImageField(_('фото'), upload_to = "foto")
    description = models.CharField(_('описание'), max_length=255, blank=True, null=True,  help_text='ввести краткое (255 символов) описание фотографии')
    observation = models.ForeignKey('Observation', verbose_name='обследование', help_text='выбрать Обследование', null=True, blank=True, on_delete=models.CASCADE)
    #hidden fields
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, default='ufo', help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)


    def __str__(self):
        return self.image.url
    
    def image_tag(self):
        return mark_safe('<img src="%s" height="450px"/>' % self.image.url)
    
    image_tag.allow_tags = True

    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(Foto, self).save(*args, **kwargs)
        # search vector stuff
        Foto.objects.filter(id=self.id).update(
            search_vector=Subquery(Foto.objects.filter(id=OuterRef('id')).annotate(
                search_vector_name=SearchVector(
                    "description", "observation__poi__nom", "observation__vzu__name"
                    ) 
                ).values('search_vector_name')[:1]) )


class Poi(models.Model):
    class Meta:
        verbose_name = 'Точка'
        verbose_name_plural = "точки"

    typo = models.ForeignKey('spr_type', verbose_name=_("тип"), default = 1, on_delete=models.CASCADE)
    vzu = models.ForeignKey('spr_vzu', verbose_name=_("ВЗУ"), null=True, blank=True, on_delete=models.CASCADE)
    nom = models.CharField(verbose_name=u'номер', max_length=255, help_text='указать номер скважины')
    gvk = models.CharField(verbose_name=u'номер ГВК', max_length=255, null=True, blank=True, help_text='указать номер по Государственному водному кадастру')
    height = models.FloatField(verbose_name=_('абс.отм'), help_text='указать абсолютную отметку', null=True, blank=True)
    geom = models.PointField(null=True, blank=True, help_text='указать точку, например: SRID=4326;POINT(37.573866731132966 55.78122028929206 120)')
    geom_error = models.FloatField(verbose_name=_('погрешность, м'), null=True, blank=True, help_text="указать погрешность замера координат", validators=[validate_positive_float])
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, null=True, blank=True, help_text='Пользователь создавший запись (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший запись (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return f'{self.nom} - {self.vzu.name if self.vzu.name else "без ВЗУ"} {self.typo} {self.gvk if self.gvk else ""}'

    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            try:
                self.author = user.username
            except Exception:
                pass
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(Poi, self).save(*args, **kwargs)
        # search vector stuff
        Poi.objects.annotate(search_vector_name=SearchVector("nom", 'extra', AsGeoJSON('geom') ) ).filter(
            id=self.id).update(search_vector=F("search_vector_name"))


class Observation(models.Model):
    class Meta:
        verbose_name = 'Обследование'
        verbose_name_plural = "обследования [скважин]"

    date_end = models.DateField(verbose_name=_('Дата обследования'), null=True, blank=True, help_text='введите дату обследования')
    depth = models.FloatField(verbose_name=_('глубина, м'), null=True, blank=True, validators=[validate_positive_float], help_text='указать глубину скважины по результатам обследования')
    height_cap = models.FloatField(verbose_name=_('оголовок, см'), null=True, blank=True, validators=[validate_positive_float], help_text='указать высоту оголовка от поверхности земли по результатам обследования')
    pump = models.ForeignKey('spr_pumps', verbose_name=_('марка насоса'), null=True, blank=True, on_delete=models.CASCADE, help_text='выбрать марку насоса')
    pump_depth = models.FloatField(verbose_name=_('загрузка, м'), null=True, blank=True, validators=[validate_positive_float], help_text='указать глубину загрузки насоса по результатам обследования')
    state = models.ForeignKey('spr_type', verbose_name='состояние', null=True, blank=True, help_text='выбрать состояние скважины', on_delete=models.CASCADE, related_name='observation_poi_state')
    econ_osv = models.BooleanField(_('оборотно-сальдовая ведомость?'), default=False, blank=True, help_text="указать есть ли Оборотно-сальдовая ведомость (Выписка БУ)?")
    econ_pts = models.BooleanField(_('перечень тех.средств?'), default=False, blank=True, help_text="указать есть ли Перечень тех средств?")
    econ_ppog = models.BooleanField(_('предложения по обоснованию границ?'), default=False, blank=True, help_text="указать есть ли Перечень тех средств?")
    econ_dppog = models.BooleanField(_('дополнение к предложению?'), default=False, blank=True, help_text="указать есть ли Дополнение к предложению заявителя?")
    econ_ztopo = models.BooleanField(_('записка к топоплану?'), default=False, blank=True, help_text="указать есть ли Пояснительная записка к топоплану?")
    econ_vbu = models.BooleanField(_('выписка БУ?'), default=False, blank=True, help_text="указать есть ли Выписка БУ?")
    poi = models.ForeignKey('Poi', verbose_name=_('точка'), on_delete=models.CASCADE)
    typo = models.ForeignKey('spr_type', verbose_name=_("тип обследования"), null=True, blank=True, on_delete=models.CASCADE)
    vzu = models.ForeignKey('spr_vzu', verbose_name='ВЗУ', null=True, blank=True, on_delete=models.CASCADE)
    datasource = models.ForeignKey('spr_datasource', verbose_name=_("источник данных"), null=True, blank=True, on_delete=models.CASCADE)
    passport = models.FileField(verbose_name='PDF', upload_to='passport', null=True, blank=True, validators=[validate_file_extension_pdf], help_text='Ссылка на PDF с паспортом, если есть')
    note = models.TextField(verbose_name=_('примечание'), null=True, blank=True)
    extra = JSONField(verbose_name='extra', null=True, blank=True, help_text="неструктуированные данные")
    fotos = GenericRelation('Fotos', verbose_name=_('фото'), help_text="выбрать фото")
    #hidden fields
    history = HistoricalRecords()
    remote_addr = models.GenericIPAddressField(null=True, blank=True, editable=False, help_text='IP адрес последнего отредактировавшего (заполняется автоматически)')
    created = models.DateTimeField(editable=False, verbose_name=u'Создана', null=True, blank=True, help_text='Дата-время создания (заполняется автоматически)')
    modified = models.DateTimeField(editable=False, verbose_name=u'Отредактирована', null=True, blank=True, help_text='Дата-время последнего редактирования (заполняется автоматически)')
    author = models.CharField(verbose_name='Кто создал', editable=False, max_length=255, null=True, blank=True, help_text='Пользователь создавший точку (заполняется автоматически)')
    lastuser = models.ForeignKey(get_user_model(), null=True,  blank=True, editable=False, related_name='poi_lastuser', on_delete=models.CASCADE, help_text='Последний пользователь, редактировавший точку (заполняется автоматически)')
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, verbose_name=u'UUID', help_text='Если вы не знаете что это - значит оно вам не надо')
    search_vector = SearchVectorField(null=True, editable=False)

    def image_tag(self):
        return mark_safe(f'<embed src="{self.passport.url}" type="application/pdf" height="700px" width="500">')
    
    image_tag.allow_tags = True
    
    def __str__(self):
        return str(f'Обследование Скважина №{self.poi}')

    def save(self, *args, **kwargs):
        try:
            request = get_current_request()
            user = get_current_user()
        except Exception:
            request, user = None, None
        # new object
        if not self.created:
            self.created = timezone.now()
            self.author = user.username
        # existing object
        self.modified = timezone.now()
        self.lastuser = user
        # IP stuff
        if request:
            try:
                if len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 2:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                elif len(request.META['HTTP_X_FORWARDED_FOR'].split(',')) == 1:
                    self.remote_addr = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    self.remote_addr = None
            except Exception:
                pass
        super(Observation, self).save(*args, **kwargs)
        # search vector stuff
        Observation.objects.filter(id=self.id).update(
            search_vector=Subquery(Observation.objects.filter(id=OuterRef('id')).annotate(
                search_vector_name=SearchVector(
                    "poi__nom", "typo__name", "vzu__name", "note", "datasource__name", "extra"
                    ) 
                ).values('search_vector_name')[:1]) )