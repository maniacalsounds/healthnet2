from django.contrib import admin
from .models import Entry, EntryManager

class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'date')
    list_filter = ('message', 'date')

# Register your models here.
admin.site.register(Entry, EntryAdmin)