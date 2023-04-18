from django.urls import path, include
from legacy.api.views import *
from gwm.api.views import *
from rest_framework import routers

app_name = 'gwm'

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register('spr_entity', spr_entityCRUD)
router.register('spr_type', spr_typeCRUD)


urlpatterns = [
    path('api/poi-auto', PoiAuto.as_view(), name='api-poi-auto'),
    path('api/', include(router.urls)),
]