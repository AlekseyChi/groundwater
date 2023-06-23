from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import WellsEfwView, WellsRegimeView

urlpatterns = [
    path("regime/", WellsRegimeView.as_view(), name="regime"),
    path("efw/", WellsEfwView.as_view(), name="efw"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
