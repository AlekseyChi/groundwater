from django.contrib.gis import admin
from .models import *
from django.utils.safestring import mark_safe
from suit.widgets import AutosizedTextarea
from import_export.admin import ImportExportModelAdmin



@admin.register(Kursk_wells)
class Kursk_wellsAdmin(admin.OSMGeoAdmin, ImportExportModelAdmin):
    readonly_fields = ('id', )
    search_fields = ['VZU', 'MPV']
    list_filter = ['Well_type', 'Well_cond', 'VZU', 'MPV', 'Aq_index']
    suit_list_filter_horizontal  = ('Well_type', 'Well_cond', 'VZU', 'MPV', 'Aq_index')
    list_display = ('id', 'Well_Name', 'GVK',  'Well_type', 'VZU', 'MPV', 'Aq_index', 'prim')

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'Well_Name', 'Well_type', 'Well_cond',  
            'GVK', 'MPV', 'VZU', 'Owner', 'RGF_ID']        
            }),
        ('geom', {
            'classes': ('suit-tab', 'suit-tab-geom',),
            'fields': ['geom',]
        }),            
        ('Запасы', {
            'classes': ('suit-tab', 'suit-tab-reserves',),
            'fields': ['Intake_A', 'Intake_B', 'Intake_C1','Aq_Name', 'Aq_index',]
        }),
        ('Примечания', {
            'classes': ('suit-tab', 'suit-tab-footnote',),
            'fields': ['prim',]
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id',]
            }),          
        ]

    suit_form_tabs = (
        ('general', 'General'), ('geom', 'Геометрия точки'),
        ('reserves', 'Запасы'),('footnote', 'Примечания'),
        ('readonly', 'Read only fields')
        )


@admin.register(spr_geol_index)
class spr_geol_indexAdmin(ImportExportModelAdmin):
    readonly_fields = ('code', )
    search_fields = ['header', 'article']
    list_filter = ['header',]
    list_display = ('code', 'header', 'article')


@admin.register(geolinkVZU)
class geolinkVZUAdmin(ImportExportModelAdmin):
    readonly_fields = ('code', )
    search_fields = ['header', 'article']
    list_filter = ['header',]
    list_display = ('code', 'header', 'article')


@admin.register(topo500mRus)
class topo500mRusAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    readonly_fields = ('gid', 'name',  )
    list_display = ('gid', 'name', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permision(self, request, obj=None):
        return False  

    fieldsets = [
        (None, {
            'fields': ['gid', 'id', 'name', 'geom',]
        }),
        ]


@admin.register(topo250mRus)
class topo250mRusAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    readonly_fields = ('gid', 'name',  )
    list_display = ('gid', 'name', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permision(self, request, obj=None):
        return False  

    fieldsets = [
        (None, {
            'fields': ['gid', 'id', 'name', 'geom',]
        }),
        ]  


@admin.register(Spatial)
class SpatialAdmin(admin.ModelAdmin):
    class Meta:
        widgets = {
            'srtext': AutosizedTextarea(attrs={'rows': 2}),
            'proj4text': AutosizedTextarea(attrs={'rows': 2}),
        }
    search_fields = ['proj4text', 'srtext', 'auth_srid']
    list_display = ('srid', 'auth_name', 'auth_srid', 'proj4text')
    list_filter  = ('auth_name', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permision(self, request, obj=None):
        return False  