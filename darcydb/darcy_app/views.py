from rest_framework import generics, mixins, status
from rest_framework.response import Response
from .models import WellsRegime, WellsEfw
from .serializers import WellsRegimeSerializer, WellsEfwSerializer, WellsWaterDepthSerializer
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, HttpResponse
from django.views import View
from django.conf import settings
import os

class WellsRegimeView(mixins.ListModelMixin,
                                    mixins.CreateModelMixin,
                                    mixins.UpdateModelMixin,
                                    generics.GenericAPIView):
    queryset = WellsRegime.objects.all()
    serializer_class = WellsRegimeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WellsEfwView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   generics.GenericAPIView):
    queryset = WellsEfw.objects.all()
    serializer_class = WellsEfwSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)



