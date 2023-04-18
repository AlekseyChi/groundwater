from import_export import resources
from .models import *

class spr_entityResource(resources.ModelResource):
    model = spr_entity
    fields = ('id', 'name', 'extra',)

class spr_typeResource(resources.ModelResource):
    model = spr_type
    fields = ('id', 'name', 'apply_to', 'extra',)
