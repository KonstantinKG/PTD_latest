import json
from .models import *
from main.mixins import *
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from django.db.models import Sum, F
from django.http import JsonResponse, HttpResponseServerError

# Create your views here.

def tours(request):
   return render(request, 'tournaments/tournaments.html')

class TournamentView(ListView, DataMixin):
   model = Tournament
   template_name = 'tournaments/tournaments.html'
   context_object_name = 'tours'
   paginate_by = 4
   template = 'tournaments/tournaments.html'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Турниры',
         curr_page_url='tours'
      )
      return dict(list(context.items()) + list(c_def.items()))

   def get_queryset(self):
      return cache.get_or_set('tours', Tournament.objects.all().select_related('mode'), 60 * 10)

      

class  SingleTournamentView(DetailView, DataMixin):
   model = Tournament
   template_name = 'tournaments/tournament.html'
   slug_url_kwarg = 'tour_slug'
   context_object_name = 'tour'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Турниры',
         curr_page_url='tours',
         players = cache.get_or_set('players', self._get_players(), 60 * 10),
         through_model=cache.get_or_set('through_model', self._get_teams(), 60 * 10),
         self_user_tours = len(self.request.user.tournament.all()) if self.request.user.is_authenticated else None,
      )
      return dict(list(context.items()) + list(c_def.items()))

   def get_queryset(self):
      return Tournament.objects.all().select_related('mode').prefetch_related('players')

   def post(self, request, tour_slug):
      tour = self.get_object()

      if (tour.typo == '1'):
         if self.request.user in tour.players.all():
            tour.players.remove(self.request.user)
            return JsonResponse({'succes': 'Вы успешно удалены с турнира'})
         else:
            tour.players.add(self.request.user)
            return JsonResponse({'succes': 'Вы успешно добавлены на турнир'})
      else:
         if 'players' in self.request.POST:
            players = self.request.POST.getlist('players')

            if len(players) != int(tour.typo):
               return JsonResponse({'error': 'Неправильное кол-во игроков'})
            
            through_model = TeamParticapation.objects.create(tournament=tour, team=self.request.user.team)
            for index in players:
               player = User.objects.get(pk=index)

               through_model.particapants.add(player)
            
            return JsonResponse({'succes': 'Команда успешно добавлена на турнир'})
         else:
            through_model = TeamParticapation.objects.get_or_create(tournament=tour, team=self.request.user.team)

            if (through_model[1]):
               for player in self.request.user.team.players.all():
                  through_model[0].particapants.add(player)
               return JsonResponse({'succes': 'Команда успешно добавлена на турнир'})

            else:
               try:
                  TeamParticapation.objects.get(tournament=tour, team=self.request.user.team).delete()
                  return JsonResponse({'succes': 'Команда успешно удалена с турнира'})
               except:
                  return JsonResponse({'error': 'Ошибка на сервере'})

   def _get_teams(self):
      if self.object and int(self.object.typo) > 1:
         teams = self.object.particapants.all().select_related('tournament').prefetch_related('particapants').annotate(summ = Sum(F('particapants__gold') + F('particapants__silver') + F('particapants__bronze')))
         total = len(teams)

         is_leader = False
         is_less_players = False
         is_enough_players = False
         team_playing = False 

         if self.request.user.is_authenticated:
            if len(TeamParticapation.objects.filter(tournament=self.object, team=self.request.user.team)) > 0:
               team_playing = True

            is_leader = False
            if self.request.user.team:
               is_leader = self.request.user == self.request.user.team.leader
         
         if (is_leader and not team_playing):
            self_team = self.request.user.team.players.all()

            is_enough_players = len(self_team) == int(self.object.typo)

            if (not is_enough_players):
               is_less_players = len(self_team) < int(self.object.typo)

         return {
            "fields": teams,
            "total": total,
            'is_self_team_playing': team_playing,
            'is_user_leader': is_leader,
            'is_enough_players': is_enough_players,
            'is_less_players': is_less_players,
         }

      return None

   def _get_players(self):
      if self.object and int(self.object.typo) == 1:
         players = self.object.players.all()
         return {
            'data': players,
            'total': len(players)
         }

      return None

   def _get_request_user_tours(self):
      if self.request.user.is_authenticated:
         print(self.request.user)
         return self.request.user.tournament.all()
      
      return None

class SaveTourTable(View):
   def post(self, request, tour_slug):
      if request.user.is_superuser:
         data = json.load(request)['data']
         try:
            tour = Tournament.objects.get(slug=tour_slug)
            tour.table = json.dumps(data)
            tour.save()

            return JsonResponse({'message': 'Турнирная таблица успешно изменена'})
         except:
            return JsonResponse({'message': 'На сервере произошла ошибка'})
      else:
         return JsonResponse({'message': 'Вы не являетесь администратором'})