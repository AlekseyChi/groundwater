#from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField

from django.contrib.auth import get_user_model
from ..models import *
from django.contrib.gis.geos import Point
from rest_framework import serializers
#from rest_framework_gis.filters import GeometryFilter
#from rest_framework_gis.filterset import GeoFilterSet
#from django_filters import filters


__all__ = ['googleHeigthSerializer', ]


class googleHeigthSerializer(serializers.Serializer):
    elevation = serializers.CharField()