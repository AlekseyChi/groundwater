#from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.contrib.auth import get_user_model
from gwm.models import *
from django.contrib.gis.geos import Point
from rest_framework import serializers
#from rest_framework_gis.filters import GeometryFilter
#from rest_framework_gis.filterset import GeoFilterSet


__all__ = ['spr_entitySerializer', 'spr_typeSerializer']


class spr_entitySerializer(serializers.ModelSerializer):
    class Meta:
        model = spr_entity
        fields = ('id', 'name',)


class spr_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = spr_type
        fields = ('id', 'name', 'apply_to')