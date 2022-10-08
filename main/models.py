import os
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from datetime import datetime, timezone
from PTD import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.defaultfilters import slugify
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from .managers import UserManager

# import locale
# locale.setlocale(
#    category=locale.LC_ALL,
#    locale="ru-RU" 
# )

# ПОЛЬЗОВАТЕЛЬ
class User(AbstractBaseUser, PermissionsMixin):
   nickname = models.CharField(unique=True, max_length=32, verbose_name='Никнейм')
   name = models.CharField(max_length=32, blank=True, verbose_name='Имя')
   about = models.TextField(blank=True, verbose_name="О себе")
   email = models.EmailField(unique=True, verbose_name='Email')
   telephone = models.CharField(max_length=30, blank=True, verbose_name='Телефон')
   uid = models.CharField(max_length=19, unique=True, verbose_name='UID')
   photo = models.ImageField(upload_to="photos/%Y/%m/%d/", null=True, blank=True, verbose_name="Фото")

   slug = models.SlugField(max_length=64, unique=True, db_index=True, verbose_name="URL")
   
   remember_me = models.BooleanField(default=False)
   user_ip = models.CharField(blank=True, max_length=100, verbose_name='IP пользователя')
   last_online = models.DateTimeField(blank=True, null=True, verbose_name='Последний раз в онлайне')
   date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
   
   instagram = models.URLField(blank=True, verbose_name='Инстаграм')
   telegram = models.URLField(blank=True, verbose_name='Телеграм')
   vkontakte = models.URLField(blank=True, verbose_name='Вконтакте')

   is_active = models.BooleanField(default=False, verbose_name='Активирован аккаунт')
   is_staff = models.BooleanField(default=False, verbose_name='Доступ как сотрудник')
   is_superuser = models.BooleanField(default=False, verbose_name='Является админом')

   team = models.ForeignKey('Teams', on_delete=models.SET_NULL, blank=True, null=True, related_name='players', verbose_name='Команда')
   gold = models.IntegerField(verbose_name='Первых мест', default=0)
   silver = models.IntegerField(verbose_name='Вторых мест', default=0)
   bronze = models.IntegerField(verbose_name='Третьих мест', default=0)

   position = models.ForeignKey('Position', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Должность')
   limit = models.ForeignKey('Limit', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Лимит')
   clan = models.ForeignKey('Clan', on_delete=models.SET_NULL, blank=True, null=True, related_name='users', verbose_name='Клан')

   objects = UserManager()

   USERNAME_FIELD = 'nickname'
   REQUIRED_FIELDS = ['email', 'telephone', 'uid']

   class Meta:
      verbose_name = 'Пользователи'
      verbose_name_plural = 'Пользователи'
      unique_together = ('email','uid')

   def __str__(self):
      return self.nickname

   def save(self, *args, **kwargs):
      self.slug = slugify(self.nickname)

      if not self.is_superuser and self.limit is None:
         self.limit = Limit.objects.get_or_create(name='Обычный')[0]

      super(User, self).save(*args, **kwargs)

   def get_absolute_url(self):
      return reverse('profile', kwargs={'user_slug': self.slug})

   def is_online(self):
      if self.last_online:
         return (timezone.now() - self.last_online) < timezone.timedelta(minutes=5)
      return False

   def extend_online(self):
      if not self.is_online():
         self.last_online = datetime.now()
         self.save()

   def get_full_name(self):
      '''
      Returns the first_name plus the last_name, with a space in between.
      '''
      return self.name.strip()

   def get_short_name(self):
      '''
      Returns the short name for the user.
      '''
      short_name = self.name.split(' ')[0]
      return short_name.strip()

   def email_user(self, subject, message, from_email=None, **kwargs):
      '''
      Sends an email to this User.
      '''
      send_mail(subject, message, from_email, [self.email], **kwargs)

# КОМАНДЫ
class Teams(models.Model):
   name = models.CharField(unique=True, max_length=64, verbose_name='Название')
   leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Лидер')

   class Meta:
      verbose_name = 'Команду'
      verbose_name_plural = 'Команды'

   def __str__(self):
      return self.name

   def clean(self):
      leader = self.leader

      if leader.team is not None and leader.team != self:
         raise ValidationError({'__all__': 'Вы являетесь лидером другой команды.'})
   
   def save(self, *args, **kwargs):
      super(Teams, self).save(*args, **kwargs)
      self.leader.team = self
      self.leader.save()

# УЧАСТИЕ КОМАНД НА ТУРНИРЕ
class TeamParticapation(models.Model):
   team = models.ForeignKey('Teams', on_delete=models.PROTECT, related_name='teams', verbose_name='Команда')
   particapants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name='Участники')
   tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='particapants', verbose_name='Турнир')

   class Meta:
      verbose_name = 'Участие в турнире'
      verbose_name_plural = 'Участие в турнирах'
      unique_together = ('team','tournament')

# ПРИГЛАШЕНИЯ В КОМАНДУ
class Invitations(models.Model):
   team = models.ForeignKey('Teams', on_delete=models.CASCADE)
   player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

   class Meta:
      verbose_name = 'Приглашение'
      verbose_name_plural = 'Приглашения'

# ДОЛЖНОСТЬ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
class Position(models.Model):
   name = models.CharField(max_length=32, unique=True, verbose_name='Название должности')
   color = models.CharField(max_length=7, default='#C5C5C5', verbose_name='Цвет')
   priority = models.SmallIntegerField(verbose_name='Приоритет', unique=True, help_text='Чем ниже приоритет тем главнее должность')

   class Meta:
      verbose_name = 'Должность'
      verbose_name_plural = 'Должности'
      ordering = ['id']

   def __str__(self):
      return self.name

# КЛАН
class Clan(models.Model):
   name = models.CharField(max_length=124, unique=True, verbose_name='Название клана')
   maximum = models.PositiveSmallIntegerField(verbose_name='Максимум игроков', default=50)

   class Meta:
      verbose_name = 'Клан'
      verbose_name_plural = 'Кланы'
      ordering = ['id']

   def __str__(self):
      return self.name

# ОГРАНИЧЕНИЯ
class Limit(models.Model):
   name = models.CharField(max_length=32, unique=True, verbose_name='Название лимита',  default='Обычный')
   invitations = models.PositiveSmallIntegerField(verbose_name='Лимит на кол-во приглашений в команду', default=15)
   tournaments = models.PositiveSmallIntegerField(verbose_name='Лимит на кол-во участий в турнирах', default=6)

   class Meta:
      verbose_name = 'Лимит'
      verbose_name_plural = 'Ограничения'
      ordering = ['id']

   def __str__(self):
      return self.name

# НОВОСТИ
class News(models.Model):
   image = models.ImageField(upload_to="news/%Y/%m/%d/", null=True, blank=True, verbose_name="Изображение")
   data = models.FileField(upload_to="news/%Y/%m/%d/",null=True, blank=True, verbose_name="Файл")
   title = models.CharField(max_length=500, verbose_name='Заголовок')
   content = models.TextField(verbose_name='Текст новости', help_text='Если вы копируете текст из сторонних источников и вставляете в это поле не забывается нажимать кнопку Т с крестиком снизу')

   date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
   is_published = models.BooleanField(default=True, verbose_name="Опубликовать")

   slug = models.SlugField(max_length=500, unique=True, db_index=True, verbose_name="URL")

   class Meta:
      verbose_name = 'Новость'
      verbose_name_plural = 'Новости'
      ordering = ['-date']

   def __str__(self):
      return self.title

   def get_absolute_url(self):
      return reverse('new', kwargs={'new_slug': self.slug})

   def get_date(self):
      date = self.date.replace(tzinfo=None)
      date_now = datetime.now().replace(tzinfo=None)
      month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
         'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
         
      if date_now.now().month != date.month:
         return f'{date.day} {month_list[date.month-1]}'

      if date_now.now().day == date.day:
         return 'Сегодня'
      elif date_now.now().day - date.day == 1:
         return 'Вчера'
      else: 
         return f'{date.day} {month_list[date.month-1]}'

   

# НАСТРОЙКА ГЛАВНОЙ СТРАНИЦЫ
class AboutPageModel(models.Model):
   video = models.FileField(upload_to="about/videos/", null=True, blank=True, verbose_name="Видео")
   para1 = models.TextField(verbose_name="Параграф 1-й")
   para2 = models.TextField(blank=True, verbose_name="Параграф 2-й")

   class Meta:
      verbose_name = 'О клане'
      verbose_name_plural = 'О клане'

   def __str__(self):
      return 'Настройки страницы "О клане"'

   def clean(self):
      exist_models = AboutPageModel.objects.filter(pk=self.pk)
      avail_video_formats = [".mp4", ".webm", ".ogg"]

      if not self.video:
         return

      if os.path.splitext(self.video.url)[1] not in avail_video_formats:
         raise ValidationError({'video': 'Не правильный формат файла. Поддерживаемые: .mp4", ".webm", ".ogg'})

      if len(exist_models) > 0:
         if exist_models[0].pk != self.pk:
            raise ValidationError({'__all__': 'Невозможно создать вторую запись.'})

# ХРАНИТ ФОТО ДЛЯ СЛАЙДЕРА
class AboutPagePhotos(models.Model):
   photo = models.ImageField(upload_to="about/images/", verbose_name="Фото")
   page = models.ForeignKey(AboutPageModel, on_delete=models.PROTECT, related_name='photos')
   
   class Meta:
      verbose_name = 'Фото для слайдера'
      verbose_name_plural = 'Фото для слайдера'

   def __str__(self):
      if self.photo:
         parent_st = 'position: relative; overflow: hidden; width: 30vw; min-width: 250px; min-height: 250px; height: 30vh;'
         img_st = 'position: absolute; width: 100%; height: 100%; top: 0; left: 0; object-fit: cover;'
         
         return mark_safe(f"<div style='{parent_st}'><img src='{self.photo.url}' style='{img_st}'></div>")
