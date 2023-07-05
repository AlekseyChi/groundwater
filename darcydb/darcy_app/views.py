from rest_framework import generics, mixins

from .models import WellsEfw, WellsRegime
from .serializers import WellsEfwSerializer, WellsRegimeSerializer


class WellsRegimeView(
    mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView
):
    queryset = WellsRegime.objects.all()
    serializer_class = WellsRegimeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WellsEfwView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = WellsEfw.objects.all()
    serializer_class = WellsEfwSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
