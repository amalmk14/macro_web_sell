from django.contrib import admin
from .models import *

# Register your models here.

class TypeAdmin(admin.ModelAdmin):
    list_display = ['name','slug']
    prepopulated_fields = {'slug':('name',)}
admin.site.register(TemplatesType,TypeAdmin)

admin.site.register(Templates)
admin.site.register(Orders)

admin.site.register(Coupen_code)