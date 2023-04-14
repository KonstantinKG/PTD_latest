import json
from datetime import date
from django.db import models
from main.models import User, Teams, TeamParticapation
from PTD import settings
from django.urls import reverse
from django.core.exceptions import ValidationError

# Create your models here.

class Tournament(models.Model):
   TYPO_CHOICES = [
      ("1", '1vs1'),
      ("2", '2vs2'),
      ("3", '3vs3'),
      ("4", '4vs4'),
      ("5", '5vs5')
   ]

   title = models.CharField(max_length=255, unique=True, verbose_name='Название')
   description = models.TextField(verbose_name='Описание')
   rules = models.TextField(verbose_name='Правила')
   places = models.SmallIntegerField(verbose_name='Кол-во мест на турнире', default=15)
   min_places = models.SmallIntegerField(verbose_name='Mинимальное кол-во участников', default=15)
   photo = models.ImageField(upload_to="photos/%Y/%m/%d/", null=True, blank=True, verbose_name="Фото")
   typo = models.CharField(max_length=64, choices=TYPO_CHOICES, default='1vs1', verbose_name='Тип турнира')
   mode = models.ForeignKey('Mode', on_delete=models.PROTECT, verbose_name='Режим')
   status = models.ForeignKey('Status', on_delete=models.PROTECT, verbose_name='Статус')
   date_start = models.DateField(verbose_name='Дата начала')
   date_end = models.DateField(verbose_name='Дата завершения')

   is_published = models.BooleanField(default=True, verbose_name="Опубликовать")

   slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

   players = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='tournament', verbose_name='Учавствующие игроки')

   table = models.JSONField(blank=True, null=True)

   class Meta:
      verbose_name = 'Турнир'
      verbose_name_plural = 'Турниры'
      ordering = ["date_start", "date_end", 'status__priority']


   def __str__(self):
      return self.title

   def get_absolute_url(self):
      return reverse('tour', kwargs={'tour_slug': self.slug})

   def get_typo_str(self):
      if int(self.typo) == 1:
         return 'Одиночный турнир 1vs1'
      else:
         return f'Командный турнир {self.typo}vs{self.typo}'

   def get_date(self):
      date_start = self.date_start
      date_end = self.date_end

      month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
         'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

      return f'{date_start.day} {month_list[date_start.month-1]} - {date_end.day} {month_list[date_end.month-1]}'

   def check_is_started(self):
      if self.status.code == Status.PLAYING:
         return True
      return False

   def check_is_closed(self):
      if self.date_end < date.today() or self.status.code == Status.CLOSED:
         return True
      return False

   def clean(self):
      if (self.places < self.min_places):
         self.places = self.min_places
      
      tour = Tournament.objects.filter(slug=self.slug)

      if (len(tour) == 0):
         print("len")
         self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['open'], code=Status.OPEN, priority=1)[0]
         return

      status = tour[0].status
      print("Open")
      if status.code == Status.OPEN or status.code == Status.CLOSING:
         print("1")
         self._check_soon_start()
         self._check_open_spaces()

         if self.typo != tour[0].typo:
            self._delete_particapants(tour[0])

      elif status.code == Status.PLAYING:
         print("2")
         if not self._check_table_changes(tour[0]):
            raise ValidationError({'__all__': 'Изменение турнира невозможно во время когда турнир активен'})

      elif status.code == Status.CLOSED:
         print("3")
         if status.name == settings.STATUS_MSG['failed']:
            
            if self.typo != tour[0].typo:
               self._delete_particapants(tour[0])

            if not self._check_soon_start():
               self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['open'], code=Status.OPEN, priority=1)[0]
         
         elif not self._check_table_changes(tour[0]):
            raise ValidationError({'__all__': 'Изменение турнира после его удачного завершения невозможно'})

   # Добавляет и убирает очки победителям
   def _set_points(self, obj, desc=False):
      for key in obj:
         user = User.objects.get(nickname=obj[key])
         val = -1 if desc else 1
         if key == 'gold':
            user.gold += val
         elif key == 'silver':
            user.silver += val
         elif key == 'bronze':
            user.bronze += val

         user.save()

   def _delete_particapants(self, tour):
      # Если соло турнир удаляем игроков
      if tour.typo == '1':
         tour.players.clear()

      # Иначе команды
      else:
         for tp in TeamParticapation.objects.filter(tournament=tour):
            tp.delete()
      
   # Проверяет заполненость турнира
   def _check_open_spaces(self):
      total = 0
      if self.typo == '1':
         total = self.players.count()
      else:
         total = self.particapants.count()

      if total / self.places >= 0.6:
         self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['low_spaces'], code=Status.CLOSING, priority=2)[0]
      else:
         if self.status.name == settings.STATUS_MSG['low_spaces']:
            self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['open'], code=Status.OPEN, priority=1)[0]

   # Проверяет скоро ли начало
   def _check_soon_start(self):
      if (self.date_start - date.today()).days <= 2:
         self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['soon_start'], code=Status.CLOSING, priority=3)[0]
         return True
      else:
         if self.status.name == settings.STATUS_MSG['soon_start']:
            self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['open'], code=Status.OPEN, priority=1)[0]
         return False

   # Проверяет если в турнирной таблице произошли изменения
   def _check_table_changes(self, tour):
      if (self.table is None):
         return False

      saving_table = json.loads(self.table)

      if (tour.table is not None):
         existing_table = json.loads(tour.table)

         if existing_table == saving_table:
            return False

         old_winners = {
            "gold": existing_table['first'],
            "silver": existing_table['second'],
            "bronze": existing_table['third']
         } 
         new_winners = {
            "gold": saving_table['first'],
            "silver": saving_table['second'],
            "bronze": saving_table['third']
         } 

         if old_winners['gold'] != '' and old_winners['silver'] != '' and old_winners['bronze'] != '':
            self._set_points(old_winners, True)

         if new_winners['gold'] != '' and new_winners['silver'] != '' and new_winners['bronze'] != '':
            print("status")
            self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['finished'], code=Status.CLOSED, priority=5)[0]
            self._set_points(new_winners)

      else: 
         winners = {
            "gold": saving_table['first'],
            "silver": saving_table['second'],
            "bronze": saving_table['third']
         } 
         if winners['gold'] != '' and winners['silver'] != '' and winners['bronze'] != '':
            self.status = Status.objects.get_or_create(name=settings.STATUS_MSG['finished'], code=Status.CLOSED, priority=5)[0]
            self._set_points(winners)
            
      return True


class Mode(models.Model):
   name = models.CharField(max_length=255, unique=True, verbose_name='Название режима')
   abbr = models.CharField(max_length=20)

   class Meta:
      verbose_name = 'Режим'
      verbose_name_plural = 'Режимы'

   def __str__(self):
      return self.name

   def save(self):
      self._create_abbreviation(self.name)

      super(Mode, self).save()

   def _create_abbreviation(self, msg):
      if self.abbr != '': return

      temp = ''
      msg = msg.strip().split(' ')
      
      for ms in msg:
         temp += ms[0].strip()

      self.abbr = temp.upper()


class Status(models.Model):
   OPEN = 'green'
   CLOSING = 'yellow'
   PLAYING = 'orange'
   CLOSED = 'red'

   CODE_CHOICES = [
      (OPEN, 'OPEN'),
      (CLOSING, 'CLOSING'),
      (PLAYING, 'PLAYING'),
      (CLOSED, 'CLOSED')
   ]

   name = models.CharField(max_length=255, unique=True, verbose_name='Название статуса')
   code = models.CharField(max_length=64, choices=CODE_CHOICES, default=OPEN, verbose_name='Тип статуса')
   priority = models.SmallIntegerField(unique=True, verbose_name='Приоритет')

   class Meta:
      verbose_name = 'Статус'
      verbose_name_plural = 'Статусы'

   def __str__(self):
      return self.name