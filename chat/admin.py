from django.contrib import admin
from .models import *
from main.admin import ptd_site

# Register your models here.
class MessagesAdmin(admin.ModelAdmin):
    fields = ('message', 'user', 'date_created')
    readonly_fields = ('message', 'user', 'date_created')

ptd_site.register(Messages, MessagesAdmin)