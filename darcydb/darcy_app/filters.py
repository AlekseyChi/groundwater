# from datetime import date

from django.contrib import admin

from .models import DictDocOrganizations, DictEntities

__all__ = [
    "WellsTypeFilter",
    "TypeEfwFilter",
    "DocTypeFilter",
    "DocSourceFilter",
    "DictEquipmentTypeFilter",
    "BalanceTypeFilter",
]


class BalanceTypeFilter(admin.SimpleListFilter):
    title = "Тип подземных вод"
    parameter_name = "typo"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity__name="тип подземных вод").values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(typo=self.value())
        else:
            return queryset


class DictEquipmentTypeFilter(admin.SimpleListFilter):
    title = "Тип оборудования"
    parameter_name = "typo"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity__name="тип оборудования").values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(typo=self.value())
        else:
            return queryset


class WellsTypeFilter(admin.SimpleListFilter):
    title = "Тип скважины"
    parameter_name = "typo"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity__name="тип скважины").values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(typo=self.value())
        else:
            return queryset


class TypeEfwFilter(admin.SimpleListFilter):
    title = "Тип ОФР"
    parameter_name = "type_efw"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity__name="тип офр").values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type_efw=self.value())
        else:
            return queryset


class DocTypeFilter(admin.SimpleListFilter):
    title = "Тип документа"
    parameter_name = "typo"

    def lookups(self, request, model_admin):
        return DictEntities.objects.filter(entity__name="тип документа").values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(typo=self.value())
        else:
            return queryset


class DocSourceFilter(admin.SimpleListFilter):
    title = "Источник поступления"
    parameter_name = "source"

    def lookups(self, request, model_admin):
        return DictDocOrganizations.objects.values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source=self.value())
        else:
            return queryset
