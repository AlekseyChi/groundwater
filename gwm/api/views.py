from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from gwm.models import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from gwm.api.serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.contrib.gis.geos import Polygon as POLYGON
from django.contrib.gis.geos import Point as POINT
from functools import reduce
try:
    from django.utils.translation import ugettext_lazy as _
except Exception:
    from django.utils.translation import gettext_lazy as _
#from rest_framework import serializers
from django.db import connection
from rest_framework.exceptions import ParseError, APIException
from dal import autocomplete



__all__ = [
    'PoiAuto',
    'spr_typeCRUD', 'spr_entityCRUD',
]

class PoiAuto(autocomplete.Select2QuerySetView):
    '''Все Точки'''
    def get_queryset(self):
        vzu = self.forwarded.get('vzu', None)
        qs = Poi.objects.all()
        if vzu:
            try:
                qs = Poi.objects.filter(vzu=vzu)
                if self.q:
                    qs = qs.filter(nom__icontains=self.q)
            except Exception:
                pass
        if self.q:
            qs = qs.filter(nom__icontains=self.q)
        return qs


class spr_typeCRUD(ModelViewSet):
    '''Создание/редактирование Справочник Сущность'''

    model = spr_type
    queryset = spr_type.objects.all()
    serializer_class = spr_typeSerializer
    search_fields = ['name', 'extra']
    filterset_fields  = ['name', ]


class spr_entityCRUD(ModelViewSet):
    '''Создание/редактирование Справочник Сущность'''

    model = spr_entity
    queryset = spr_entity.objects.all()
    serializer_class = spr_entitySerializer
    search_fields = ['name', 'extra']
    filterset_fields  = ['name', ]


