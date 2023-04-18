from django.contrib.gis.db import models
from django.contrib.gis.db.models import PolygonField, MultiPolygonField

# Create your models here.

__all__ = ['Spatial', 'topo250mRus', 'topo500mRus', 'geolinkVZU', 'Kursk_wells', 'spr_geol_index' ]



class Kursk_wells(models.Model):
    class Meta:
        verbose_name = "Poi ВЗУ Курск"
        verbose_name_plural = "Poi ВЗУ Курск"
        db_table = 'kursk_well'
        managed = False
    
    id = models.BigIntegerField(primary_key=True)
    geom = models.PointField(srid=4326, dim=2, verbose_name=u'геометрия точки (xyz)', help_text='точки')
    fid = models.CharField(max_length=255, verbose_name='fid', null=True, blank=True)
    Well_Name = models.CharField(max_length=255, verbose_name='номер', null=True, blank=True)
    Well_type = models.CharField(max_length=255, verbose_name='тип', null=True, blank=True)
    Aq_Name = models.CharField(max_length=255, verbose_name='геология текст', null=True, blank=True)
    Aq_index = models.CharField(max_length=255, verbose_name='геология индекс', null=True, blank=True)
    #Aq_index = models.ForeignKey('spr_geol_index', to_field='header', null=True, blank=True, verbose_name='геол.индекс', on_delete=models.CASCADE)
    MPV = models.CharField(max_length=255, verbose_name='МПВ', null=True, blank=True)
    VZU = models.CharField(max_length=255, verbose_name='ВЗУ', null=True, blank=True)
    Owner = models.CharField(max_length=255, verbose_name='owner', null=True, blank=True)
    RGF_ID = models.BigIntegerField(verbose_name='RGF ID', null=True, blank=True)
    Well_cond = models.CharField(max_length=255, verbose_name='состояние', null=True, blank=True)
    Intake_A = models.FloatField(verbose_name='A', null=True, blank=True)
    Intake_B = models.FloatField(verbose_name='B', null=True, blank=True)
    Intake_C1 = models.FloatField(verbose_name='C1', null=True, blank=True)
    GVK = models.CharField(max_length=255, verbose_name='№ГВК', null=True, blank=True)
    prim = models.TextField(verbose_name='примечание', null=True, blank=True)

    def __str__(self):
        return f'{self.Well_Name} (ГВК:{self.GVK}, ВЗУ:{self.VZU}, Тип:{self.Well_type}, состояние:{self.Well_cond})'


class spr_geol_index(models.Model):
    class Meta:
        db_table = '"Kursk"."00002"'
        managed = False
        verbose_name = "Справочник Геологический индекс (read only!)"
        verbose_name_plural = "Справочник Геологический индекс (read only!)"

    code = models.BigIntegerField(primary_key=True)
    article = models.TextField(verbose_name = 'full name')
    header = models.CharField(max_length=255, verbose_name='short name', unique=True)

    def __str__(self):
        return f'{self.header}'


class geolinkVZU(models.Model):
    class Meta:
        verbose_name = "Справочник ВЗУ (read only!)"
        verbose_name_plural = "Справочник ВЗУ (read only!)"
        db_table = '"Kursk"."00010"'
        managed = False
    
    code = models.BigIntegerField(primary_key=True)
    article = models.TextField(verbose_name = 'full name')
    header = models.CharField(max_length=255, verbose_name='short name')


class Spatial(models.Model):
    class Meta:
        managed = False # таблица не будет создаваться/удаляться при миграции
        db_table = 'spatial_ref_sys'
        verbose_name = "cистему координат"
        verbose_name_plural = "cистемы координат (spatial_ref_sys - read only!)"

    srid = models.IntegerField(verbose_name='srid', primary_key=True)
    auth_name = models.CharField(verbose_name='auth_name', max_length=256)
    auth_srid = models.IntegerField(verbose_name='auth_srid')
    srtext = models.TextField(verbose_name='srtext')
    proj4text = models.TextField(verbose_name='proj4text')

    def __str__(self):
        return f'{self.auth_srid}' 


class topo250mRus(models.Model):
    class Meta:
        verbose_name = "номенклатурные номера листов 25000 (read only!)"
        verbose_name_plural = "1:25000 (read only!)"
        db_table = 'topo250m-rus'
        managed = False
    
    gid = models.BigIntegerField(primary_key=True)
    id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    geom = MultiPolygonField(srid=4284, verbose_name=u'планшет')

    def __str__(self):
            return f'{self.name}'


class topo500mRus(models.Model):
    class Meta:
        verbose_name = "номенклатурные номера листов 50000 (read only!)"
        verbose_name_plural = "1:50000 (read only!)"
        db_table = 'topo500m-rus'
        managed = False
    
    gid = models.BigIntegerField(primary_key=True)
    id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    geom = MultiPolygonField(srid=4284, verbose_name=u'планшет')

    def __str__(self):
            return f'{self.name}'