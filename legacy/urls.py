from django.urls import path, include
from legacy.api.views import *
from rest_framework import routers

app_name = 'legacy'


# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register('get-google-elevation', getGoogleHeight, 'get-google-elevation' )


urlpatterns = [
    #path('api/get-google-elevation/', getGoogleHeight.as_view(), 'get-google-elevation'),
    path('api/', include(router.urls)),
]