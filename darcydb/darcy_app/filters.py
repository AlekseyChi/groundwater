# from datetime import date

from django.contrib import admin

from .models import DictEntities

# from django.utils.translation import gettext_lazy as _


class WellsTypeFilter(admin.SimpleListFilter):
    title = "Тип скважины"
    parameter_name = "typo"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity=1).values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(typo=self.value())
        else:
            return queryset


class TypeEfwFilter(admin.SimpleListFilter):
    title = "Тип ОФР"
    parameter_name = "type_efw"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity=2).values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type_efw=self.value())
        else:
            return queryset


class DocTypeFilter(admin.SimpleListFilter):
    title = "Тип документа"
    parameter_name = "typo"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity=6).values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(typo=self.value())
        else:
            return queryset


class DocSourceFilter(admin.SimpleListFilter):
    title = "Источник поступления"
    parameter_name = "source"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity=7).values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source=self.value())
        else:
            return queryset
