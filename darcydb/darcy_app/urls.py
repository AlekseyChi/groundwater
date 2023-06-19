from .views import WellsRegimeView, WellsEfwView
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path


urlpatterns = [
    path('regime/', WellsRegimeView.as_view(), name='regime'),
    path('efw/', WellsEfwView.as_view(), name='efw'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
