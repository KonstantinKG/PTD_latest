from django.contrib import admin
from .models import *
from main.models import *
from tinymce.widgets import TinyMCE
from django import forms
from main.admin import ptd_site

# Register your models here.
class TournamentFormAdmin(forms.ModelForm):
   description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), label='Правила', help_text='Если вы копируете текст из сторонних источников и вставляете в это поле не забывайте выделить текст и нажать кнопку Т с крестиком снизу')
   rules = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), label='Правила', help_text='Рекомендовано использовать только списки в этом поле')

   class Meta:
      model = Tournament
      fields = '__all__'


# @admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
   form = TournamentFormAdmin

   list_display = ('id', 'title', 'mode', 'typo', 'status', 'date_start', 'date_end')
   list_display_links = ('id', 'title')
   search_fields = ('title',)
   list_editable = ('mode', 'typo')
   list_filter = ('mode', 'typo', 'status', 'date_start', 'date_end')
   ordering = ("date_start", "date_end", 'status__priority')
   readonly_fields = ('get_html_photo', 'status')
   prepopulated_fields = {"slug": ("title",)}

   fieldsets = (
      ('О турнире', {
         'fields': (
            'title', 'slug', 'status', 'photo', 'get_html_photo', 'description', 'rules'
         ),
      }),
      ('Характеристики турнира', {
         'fields': (
            'places', 'min_places', 'mode', 'typo', 'date_start', 'date_end'
         ),
      }),
      ('Опубликовать', {
         'fields': (
            'is_published',
         ),
      }),
      ('Участники', {
         'fields': (
            'players',
         ),
      }),
      ('Турнирная таблица', {
         'fields': (
            'table',
         ),
      }),
   )

   def get_html_photo(self, object):
      if object.photo:
         return mark_safe(f"<img src='{object.photo.url}' width=250>")
   
   get_html_photo.short_description = "Картинка"

class ModeFormAdmin(forms.ModelForm):
   abbr = forms.CharField(required=False, label='Аббревиатура', help_text='Аббревиатура создастся автоматически после сохранения или вы можете вписать ее самостоятельно. Чтобы все коректно отработало каждое новое слово вписываемое в название должно идти через пробел')

   class Meta:
      model = Mode
      fields = '__all__'

ptd_site.register(Tournament, TournamentAdmin)

# @admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
   form = ModeFormAdmin

   list_display = ('id', 'name', 'abbr')
   list_display_links = ('id',)
   search_fields = ('name', 'abbr')
   list_editable = ('name', 'abbr')
   fields = ('name', 'abbr')
   
ptd_site.register(Mode, ModeAdmin)

# @admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
   list_display = ('id', 'name', 'code')

ptd_site.register(Status, StatusAdmin)

