from django.contrib import admin
from .models import *

class EntryPersonLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'location', 'name', )
    search_fields = ('date', 'name', 'location')
    list_filter = ('date', 'name')
    fields = ('id', 'date', 'location', 'name', )
    readonly_fields = ('date', 'location', 'name')
    save_on_top = True

class EntryCarLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'location', 'number', )
    search_fields = ('date', 'number', 'location')
    list_filter = ('date', 'number')
    fields = ('id', 'date', 'location', 'number', )
    readonly_fields = ('date', 'location', 'number')
    save_on_top = True


admin.site.register(Camers)
admin.site.register(EntryPersonLog, EntryPersonLogAdmin)
admin.site.register(EntryCarLog, EntryCarLogAdmin)

admin.site.site_title = 'Админ-панель сайта Video Control'
admin.site.site_header = 'Админ-панель сайта Video Control'

