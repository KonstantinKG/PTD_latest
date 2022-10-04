from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from tinymce.widgets import TinyMCE
from django.utils.safestring import mark_safe
from django import forms
from .models import *

class PTDSite(admin.AdminSite):
   site_title = "Администрирование сайта PTD"

   # Text to put in each page's <h1>.
   site_header = "Platinum Dragons"

   # Text to put at the top of the admin index page.
   index_title = "Администрирование сайта"

ptd_site = PTDSite(name='Alo')

# Register your models here.
# @admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):

   list_display = ('id', 'nickname', 'name', 'is_staff', 'clan', 'position', 'limit')
   list_display_links = ('id', 'nickname', 'name')
   search_fields = ('nickname', 'name')
   list_editable = ('clan', 'position')
   list_filter = ('is_staff', 'clan', 'date_joined', 'position')
   ordering = ("nickname",)
   fieldsets = (
      ('Настройки пользователя', {
         'fields': (
            'clan', 'position', 'limit', 'is_staff', 'is_active', 'is_superuser' 
         ),
      }),
      ('О пользователе', {
         'fields': (
            'nickname', 'name', 'get_html_photo','about', 'email', 'telephone', 'uid', 'team', 'date_joined', 'last_online'
         ),
      }),
      ('Соц. сети', {
         'fields': (
            'instagram', 'telegram', 'vkontakte'
         ),
      }),
      ('Награды', {
         'fields': (
            'gold', 'silver', 'bronze'
         ),
      }),
   )
   readonly_fields = ('nickname', 'name', 'about', 'team',
      'get_html_photo', 'email', 'telephone', 'uid', 'is_active',
      'gold', 'silver', 'bronze', 'instagram', 'telegram', 
      'vkontakte', 'date_joined', 'last_online', 'is_superuser'
   )

   def get_html_photo(self, object):
      if object.photo:
         return mark_safe(f"<img src='{object.photo.url}' width=250>")
   
   get_html_photo.short_description = 'Фотография'

ptd_site.register(User, CustomUserAdmin)


# @admin.register(Limit)
class LimitAdmin(admin.ModelAdmin):
   list_display = ('name', 'invitations', 'tournaments')
   list_editable = ('invitations', 'tournaments')
   list_display_links = ('name',)
   list_filter = ('name',)

ptd_site.register(Limit, LimitAdmin)

# @admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
   list_display = ('name', 'leader')
   list_filter = ('name',)

ptd_site.register(Teams, TeamsAdmin)


class PositionFormAdmin(forms.ModelForm):
   color = forms.CharField(label='Цвет', widget=forms.TextInput(attrs={'type': 'color'}))

   class Meta:
      model = Position
      fields = '__all__'

# @admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
   list_display = ('name', 'color')
   list_filter = ('name',)
   form = PositionFormAdmin

ptd_site.register(Position, PositionAdmin)

# @admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
   list_display = ('name', 'maximum')
   list_filter = ('name',)

ptd_site.register(Clan, ClanAdmin)

class NewsAdminForm(forms.ModelForm):
   content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), label='Текст новости')
   class Meta:
      model = News
      fields = '__all__'

# @admin.register(News)
class NewsAdmin(admin.ModelAdmin):
   form = NewsAdminForm

   list_display = ('title', 'get_html_photo', 'is_published')
   list_display_links = ('title',)
   list_editable = ('is_published',)
   list_filter = ('date',)
   search_fields = ('title', 'slug')
   prepopulated_fields = {"slug": ("title",)}
   readonly_fields = ('date', 'get_html_photo')
   fieldsets = (
      ('Заголовок и Фото', {
         'fields': (
            'title', 'slug', 'date', 'image', 'get_html_photo' 
         ),
      }),
      ('Описание', {
         'fields': (
            'content', 
         ),
      }),
      ('Закрепленный файл', {
         'fields': (
            'data', 
         ),
      }),
      ('Опубликовать', {
         'fields': (
            'is_published', 
         ),
      }),
   )
   
   def get_html_photo(self, object):
      if object.image:
         return mark_safe(f"<img src='{object.image.url}' width=250>")
   
   get_html_photo.short_description = "Картинка"

ptd_site.register(News, NewsAdmin)


class AboutPagePhotosInline(admin.TabularInline):
   model = AboutPagePhotos

# @admin.register(AboutPageModel)
class AboutPageModelAdmin(admin.ModelAdmin):
   readonly_fields = ('get_html_video',)
   fieldsets = (
      ('Видео', {
         'fields': (
            'video', 'get_html_video'
         ),
      }),
      ('Описание', {
         'fields': (
            'para1', 'para2'
         ),
      }),
   )
   inlines = [
      AboutPagePhotosInline
   ]

   def get_html_video(self, object):
      if object.video:
         return mark_safe(f'<video width="300" height="250" controls="controls"><source src="{object.video.url}">Тег video не поддерживается вашим браузером. </video>')
         
   get_html_video.short_description = 'Загруженное видео'

ptd_site.register(AboutPageModel, AboutPageModelAdmin)