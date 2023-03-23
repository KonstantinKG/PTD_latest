import random
import json
from PTD import settings
from datetime import date
from tournaments.models import Tournament, Status
from main.models import TeamParticapation
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
   help = 'Проверяет если турнир готов для запуска'

   def handle(self, *args, **kwargs):
      tours = Tournament.objects.filter(date_start=date.today())
      
      for tour in tours:
         # Получаем участников
         particapants = ''

         if tour.typo == '1':
            particapants = list(tour.players.all())
         else:
            particapants =self._make_list_from_teams(TeamParticapation.objects.filter(tournament=tour).select_related('team')) 

         # Проверяем достаточно ли игроков
         if len(particapants) >= 3 and len(particapants) >= tour.min_places:
            random.shuffle(particapants)

            tour.table = json.dumps(self._generate_tour_table_json(particapants))
            tour.status = Status.objects.get_or_create(name=settings.STATUS_MSG['started'], code=Status.PLAYING, priority=4)[0]
            tour.save()
         else:
            tour.status = Status.objects.get_or_create(name=settings.STATUS_MSG['failed'], code=Status.CLOSED, priority=6)[0]
            tour.save()
      
      # Чистим закрытые турниры от участников
      closed_tours = Tournament.objects.filter(status__code=Status.CLOSED)

      for closed in closed_tours:
         self._delete_particapants(closed)

   def _delete_particapants(self, tour):
      # Если соло турнир удаляем игроков
      if tour.typo == '1':
         tour.players.clear()

      # Иначе команды
      else:
         for tp in TeamParticapation.objects.filter(tournament=tour):
            tp.delete()

   def _generate_tour_table_json(self, particapants):
      # Проверяем если кол-во игроков являются степенью двойки
      p_amount = len(particapants)
      is2 = self._check2rec(p_amount)
      # Если являются степенью двойки то кол-во групп это половина от участников
      # Иначе находится ближайшее число степени двойки
      groups = int(p_amount / 2 if is2 else self._find_closest_2rec(p_amount))
      
      return self._get_tour_table(particapants, groups, p_amount, is2)


   def _get_tour_table(self, particapants, groups, p_amount, is2):
      # Тело турнирной таблицы
      body={
         'stages': [],
         'first': '',
			'second': '',
			'third': ''
      }

      stage = []
      compensation = 0
      groups_length = groups

      for i in range(groups_length):
         para = {
            'player1': '',
            'score': '0,0',
            'player2': ''
         }

         # Если кол-во игроков не было степенью двойки то должны получиться полупустые группы когда кол-во игроков == кол-ву оставшихся групп
         # Так как если условие не ИСТИНА то мы создаем пару из двух игроков и из-за
         # Этого смещается  индекс следующего элемента и нужна - compensation
         if not is2 and p_amount == groups_length:
            para['player1'] = particapants[i + compensation].nickname
            compensation -= 1
         
         # Иначе создаем полную группу из двух игроков
         else:
            para['player1'] = particapants[i*2].nickname
            para['player2'] = particapants[i*2+1].nickname

            p_amount -= 2
            groups_length -= 1
            compensation = i * 2 + 1

         stage.append(para)
      body['stages'].append(stage)
      stage = []

      # Если кол-во игроков не было степенью двойки
      # То мы должны перекинуть игроков из полупустых групп на вторую стадию
      groups //= 2
      if not is2:

         for i in range(groups):
            group_upper = body['stages'][0][i * 2]
            group_lower = body['stages'][0][i * 2 + 1]
            para = {
               'player1': '',
               'score': '0,0',
               'player2': ''
            }

            if group_upper['player2'] == '':
               para['player1'] = group_upper['player1']
            if group_lower['player2'] == '':
               para['player2'] = group_lower['player1']

         stage.append(para)

         # Если осталась последняя группа нужно создать дополнительную для третьего и четвертого места
         if groups == 1:
            stage.append({
               'player1': '',
               'score': '0,0',
               'player2': ''
            })

            groups -= 1

         body['stages'].append(stage)

      # Этот цикл нужен чтобы до создать пустые группы
      while groups >= 1:
         stage = []

         for i in range(groups):
            para = {
               'player1': '',
               'score': '0,0',
               'player2': ''
            }
            stage.append(para)

         if groups == 1:
            stage.append({
               'player1': '',
               'score': '0,0',
               'player2': ''
            })

         body['stages'].append(stage)

         groups //= 2

      body['stages'].append([{'first': '', 'second': '', 'third': ''}])

      return body
   
   # Чтобы можно было работать комфортно и везде использовать nickname
   # Из модели TeamParticapation берем только название команды
   def _make_list_from_teams(self, queryset):
      temp = []

      for field in queryset:
         temp.append({
            'nickname': field.team.name
         })

      return temp

   # Проверка на степень двойки
   def _check2rec(self, num):
      if num == 1:
         return True
      if num & 1:
         return False
      
      return self._check2rec(num >> 1)

   # Нахождению ближайшего числа со степеью двойки
   def _find_closest_2rec(self, num):
      count = 1
      while num < count:
         count *= 2

      return count