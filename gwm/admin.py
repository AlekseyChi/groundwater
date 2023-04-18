from django.contrib.gis import admin
from .models import *
from .admin_resources import spr_entityResource, spr_typeResource
from django.db.models import JSONField
try:
    from jsoneditor.forms import JSONEditor
except Exception as err:
    JSONEditor = None
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
from .admin_forms import *
from django.utils.html import mark_safe
from formtools.wizard.views import SessionWizardView
from django.urls import path, re_path
from django.contrib.contenttypes.admin import GenericTabularInline


class FormWizardView(SessionWizardView):
    #template_name = "admin/spr_vzu_admin.html"
    form_list = [spr_vzuForm, ChangeReasonForm]

    def done(self, form_list, **kwargs):
        return render(self.request, 'admin/done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })

    def render_template(self, request, form, previous_fields, step, context=None):
        from django.contrib.admin.helpers import AdminForm
        # Wrap this form in an AdminForm so we get the fieldset stuff:
        form = AdminForm(form, [(
            'Step %d of %d' % (step + 1, self.num_steps()),
            {'fields': form.base_fields.keys()}
            )], {})
        context = context or {}
        context.update({
            'media': self._model_admin.media + form.media
        })
        return super(FormWizardView, self).render_template(request, form, previous_fields, step, context)
    
        
def resave(modeladmin, request, queryset):
    for qs in queryset:
        try:
            qs.save()
        except Exception as err:
            messages.error(request, str(err))
resave.short_description  = 'Пересохранить объекты'

# Register your models here.

# БАЗОВЫЕ

class FotosInlineAdmin(GenericTabularInline):
    #form = VolumeInlineForm
    model = Fotos
    extra = 5

class FotoInlineAdmin(admin.TabularInline):
    model = Foto
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector', 'image_tag')
    #list_display = ('id', 'image', 'description', 'image_tag')
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'image', 'description', 'observation', 'image_tag']        
            }),
        ]
    suit_form_tabs = (('general', 'General'),)

@admin.register(Observation)
class ObservationAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    actions = [ resave]
    form = ObservationForm
    inlines = (FotosInlineAdmin,)
    list_display = ('id', '__str__', 'poi', 'date_end', 'depth', 'typo', 'vzu', 'datasource', 'get_passport')
    list_display_links = ('__str__',)
    search_fields = ['poi__nom', 'extra', 'search_vector',]
    list_filter = ['date_end', 'created', 'modified',]
    suit_list_filter_horizontal  = ['date_end', 'created', 'modified', ]
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector', 'image_tag') 
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }
    
    def get_foto(self, obj):
        if self.obj.foto:
            return mark_safe('<img src="%s"  width="150"/>' % self.obj.foto.image.url)

    def get_passport(self, obj):
        # check for valid URL and return if no valid URL
        if obj.passport:
            #return u'есть'
            return mark_safe(f'<embed src="{obj.passport.url}" type="application/pdf">')
        else:
            return u'нет'
    get_passport.short_description = 'паспорт PDF'

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'date_end', 'vzu', 'poi', 'typo', 'state', 'depth', 'height_cap', 'pump', 'pump_depth', 'datasource', 'note' ]        
            }),
        ('Econ', {
            'classes': ('suit-tab', 'suit-tab-econ',),
            'fields': ['econ_osv', 'econ_pts', 'econ_ppog', 'econ_dppog', 'econ_ztopo', 'econ_vbu' ]
        }),
        ('Passport', {
            'classes': ('suit-tab', 'suit-tab-passport',),
            'fields': ['passport', 'image_tag']
        }),        
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (
        ('general', 'General'), ('econ', 'Экономическое'), ('passport', 'Паспорт скважины'),
        ('extra', 'Extra'), ('readonly', 'Read only fields'))


@admin.register(Foto)
class FotoAdmin(ImportExportModelAdmin):
    list_display = ('id', 'image', 'observation', 'description', )
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector', 'image_tag')
    search_fields = [ 'search_vector', 'description']
    list_filter = ['created', 'modified',]
    suit_list_filter_horizontal  = ['created', 'modified', ]
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'image', 'description', 'observation', 'image_tag']        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': []
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))


@admin.register(Poi)
class PoiAdmin(admin.OSMGeoAdmin, SimpleHistoryAdmin, ImportExportModelAdmin):
    actions = [ resave]
    form = PoiForm
    list_display = ('id', '__str__', 'nom', 'gvk', 'vzu', 'height', 'get_geom')
    list_display_links = ('__str__',)
    search_fields = ['vzu__name', 'nom', 'gvk', 'extra', 'search_vector']
    list_filter = ['vzu', 'height', 'created', 'modified']
    suit_list_filter_horizontal  = ('vzu', 'height', 'created', 'modified')
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector', 'get_geom')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    def show_x(self, obj):
        if obj.geom:
            return float(obj.geom.x)
    
    def show_y(self, obj):
        if obj.geom:
            return float(obj.geom.y)
    
    def show_z(self, obj):
        if obj.geom:
            try:
                return float(obj.geom.z)
            except Exception:
                return 'z'

    def get_geom(self, obj):
        return str(obj.geom)

    show_x.short_description = 'x (вд)'
    show_y.short_description = 'y (сш)'
    show_z.short_description = 'z (абс.отм)'
    get_geom.short_description = 'geometry'

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'vzu', 'typo', 'nom', 'gvk', 'height', ]        
            }),
        ('geom', {
            'classes': ('suit-tab', 'suit-tab-geom',),
            'fields': ['geom_error',('latitude', 'latitude_mm', 'latitude_ss'), ('longitude','longitude_mm', 'longitude_ss'), 'geom']
        }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'get_geom', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('geom', 'Геометрия'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))


@admin.register(spr_pumps)
class spr_pumpsAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    #resource_class = spr_pumpsResource
    search_fields = ['name', 'extra']
    list_filter = ['created', 'modified',]
    suit_list_filter_horizontal  = ('created', 'modified',)
    list_display = ('id', 'name', )
    list_display_links = ('name',)
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'name']        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))


@admin.register(spr_vzu)
class spr_vzuAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    #resource_class = spr_vzuResource
    search_fields = ['name', 'extra']
    list_filter = ['created', 'modified',]
    suit_list_filter_horizontal  = ('created', 'modified',)
    list_display = ('id', 'name', )
    list_display_links = ('name',)
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'name']        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))

    # попытка прикрутить FormWizard пока не удачная. 25.09.2022
    def add_view(self, request, form_url="", extra_context=None):
        view = FormWizardView.as_view(
            extra_context={"opts": self.model._meta, "media": self.media},
            form_list=[Form1, self.get_add_form(request)],
        )
        return view(request)
    

    def get_add_form(self, request):
        form = forms.modelform_factory(
            self.model,
            fields=flatten_fieldsets(self.get_fieldsets(request)),
            formfield_callback=lambda field: self.formfield_for_dbfield(field, request),
        )
        # Django's implementation of readonly is pretty complicated.
        # This is simple enough and worked for my usecase
        for field_name in self.readonly_fields:
            form.base_fields[field_name].widget.attrs["readonly"] = True 

        return form                 


    def get_urls2(self):
        urls = super().get_urls()
        view = FormWizardView.as_view()
        add_url = re_path(
            r"add/$", self.admin_site.admin_view(view), name="formwizard_add"
        )
        change_url = re_path(
            r"^(.+)/change/$",
            self.admin_site.admin_view(view),
            name="formwizard_change",
        )
        return [add_url, change_url] + urls


    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin # Save this so we can use it later.
        opts = admin.model._meta # Yes, I know we could've done spr_vzu._meta, but this is cooler :)
        self.extra_context.update({
            'title': u'Add %s' % force_unicode(opts.verbose_name),
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            'root_path': admin.admin_site.root_path,
            'app_label': opts.app_label,
        })


    

@admin.register(spr_datasource)
class spr_datasourceAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    #resource_class = spr_datasourceResource
    search_fields = ['name', 'extra']
    list_filter = ['created', 'modified',]
    suit_list_filter_horizontal  = ('created', 'modified',)
    list_display = ('id', 'name', )
    list_display_links = ('name',)
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'name']        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))


@admin.register(spr_entity)
class spr_entityAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    #resource_class = spr_entityResource
    search_fields = ['name', 'extra']
    list_filter = ['created', 'modified',]
    suit_list_filter_horizontal  = ('created', 'modified',)
    list_display = ('id', 'name', )
    list_display_links = ('name',)
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'name']        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))


@admin.register(spr_type)
class spr_typeAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    #resource_class = spr_typeResource
    search_fields = ['name', 'extra']
    list_filter = ['apply_to', 'created', 'modified']
    suit_list_filter_horizontal  = ('apply_to', 'created', 'modified')
    list_display = ('id', 'name', 'apply_to')
    list_display_links = ('name', )
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'name', 'apply_to']        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))



@admin.register(spr_change_reason)
class spr_change_reasonAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    #resource_class = spr_change_reasonResource
    search_fields = ['name', 'extra']
    list_filter = ['created', 'modified']
    suit_list_filter_horizontal  = ( 'created', 'modified')
    list_display = ('id', 'name',)
    list_display_links = ('name', )
    readonly_fields = ('id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector')
    formfield_overrides = {
        JSONField:{ 'widget': JSONEditor },
    }

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [ 'name', ]        
            }),
        ('Extra', {
            'classes': ('suit-tab', 'suit-tab-extra',),
            'fields': ['extra']
        }),
        ('Поля-для-чтения', {
            'classes': ('suit-tab', 'suit-tab-readonly',),
            'fields': ['id', 'remote_addr', 'author', 'created', 'modified', 'lastuser', 'uuid', 'search_vector']
            }),          
        ]
    suit_form_tabs = (('general', 'General'), ('extra', 'Extra'),
                 ('readonly', 'Read only fields'))                