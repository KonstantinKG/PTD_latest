import json
from .backends import *
from .forms import *
from .mixins import *
from .models import *
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.http import HttpResponse, JsonResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView

# Create your views here.

# О НАС
class AboutView(View, DataMixin):
   template = 'main/index.html'

   def get(self, request):
      request.session['last_visited_page'] = request.path_info
      return render(request, self.template, self.get_user_context(
         title='О клане',
         curr_page_url='about',
         page=AboutPageModel.objects.first()
      ))

# СОСТАВ
class MembersView(ListView, DataMixin):
   model = User
   template_name = 'main/members.html'
   context_object_name = 'hranks'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      clans = self._group_by_clans()
      c_def = self.get_user_context(
         title='Состав',
         curr_page_url='members',
         clans=clans,
         staff=User.objects.filter(is_staff=True).select_related('position')
      )
      return dict(list(context.items()) + list(c_def.items()))

   def get_queryset(self):
      return User.objects.order_by(F('position__priority').asc(nulls_last=True)).select_related('position')[:9]

   def _group_by_clans(self):
      clans = Clan.objects.annotate(total = Count('users'))
      queryset = []

      if clans:
         for clan in clans:
            if (clan is not None):
               users = User.objects.filter(clan=clan).order_by(F('position__priority').asc(nulls_last=True)).select_related('position')

               queryset.append({
                  'name': clan.name,
                  'total': clan.total,
                  'max': clan.maximum,
                  'users': users
               })

            continue
      return queryset

# НОВОСТИ
class NewsView(ListView, DataMixin):
   model = News
   template_name = 'main/news.html'
   context_object_name = 'news'
   paginate_by = 4
   template = 'main/news.html'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Новости',
         curr_page_url='news'
      )
      return dict(list(context.items()) + list(c_def.items()))

   def get_queryset(self):
      return News.objects.filter(is_published=True)

# ОТДЕЛЬНАЯ НОВОСТЬ
class  SingleNewView(DetailView, DataMixin):
   model = News
   template_name = 'main/currentNews.html'
   slug_url_kwarg = 'new_slug'
   context_object_name = 'new'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Новости',
         curr_page_url='news'
      )
      return dict(list(context.items()) + list(c_def.items()))

# ПРОФИЛЬ
class ProfileView(LoginRequiredMixin, DetailView, DataMixin):
   model = User
   template_name = 'main/profile.html'
   slug_url_kwarg = 'user_slug'
   context_object_name = 'player'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Профиль',
         invitations= self._get_invitations(),
         tournaments=self._get_user_tournaments(),
         leader = ''
      )
      return dict(list(context.items()) + list(c_def.items()))

   def get_queryset(self):
      return User.objects.all().select_related('position', 'clan', 'team')
   
   def _get_user_tournaments(self):
      if self.kwargs.get('user_slug') == self.request.user.slug:
         user = self.request.user
         solo_tours = user.tournament.all().select_related('mode')

         if user.team is not None:
            team_tours = [field.tournament for field in TeamParticapation.objects.filter(team = user.team)]

            all_tours = list(solo_tours) + team_tours
            return sorted(all_tours, key=lambda x: x.date_start, reverse=False)

         return solo_tours

      return None

   def _get_invitations(self):
      user = self.request.user
      if self.kwargs.get('user_slug') == user.slug:
         if user.team is None:
            return Invitations.objects.filter(player=self.request.user).select_related('team')

      return None
   
   def _get_leader(self):
      user = self.request.user
      if self.kwargs.get('user_slug') == user.slug:
         return user.team.leader
      
      return None

# РЕДАКТИРОВАТЬ ПРОФИЛЬ
class EditProfileView(LoginRequiredMixin, UpdateView, DataMixin):
   form_class = EditForm
   template_name='main/editProfile.html'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Профиль'
      )
      return dict(list(context.items()) + list(c_def.items()))

   def get_object(self):
      slug = self.kwargs.get('user_slug')
      return get_object_or_404(User, slug=slug)

   def form_valid(self, form):
      return super().form_valid(form)

   def form_invalid(self, form):
      return JsonResponse({'errors': form.errors})

# СОЗДАТЬ КОМАНДУ
class CreateTeamView(LoginRequiredMixin, CreateView, DataMixin):
   model=Teams
   fields = ('name', 'leader')
   template_name='main/createTeam.html'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      c_def = self.get_user_context(
         title='Команда',
         users=User.objects.all().exclude(slug=self.request.user.slug)
      )
      return dict(list(context.items()) + list(c_def.items()))

   def clean(self):
      pass

   def form_valid(self, form):
      self.object = form.save()

      self._send_invitations(self.object)

      self.request.user.team = self.object
      self.request.user.save()

      return HttpResponseRedirect(self.get_success_url())

   def get_success_url(self):
      self.success_url = self.request.user.get_absolute_url()

      if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
      return self.success_url  # success_url may be lazy

   def _send_invitations(self, team):
      players = self.request.POST.get('players', False)

      if players:
         for player in players.split(','):
            Invitations.objects.get_or_create(team=team, player=User.objects.get(pk=player))

# РЕДАКТИРОВАТЬ КОМАНДУ
class editTeamView(LoginRequiredMixin, View, DataMixin):
   template = 'main/editTeam.html'

   def get(self, request):
      team = request.user.team

      if not team:
         return HttpResponseRedirect(request.user.get_absolute_url())
      
      if (team.leader != request.user): 
         return HttpResponseRedirect(request.user.get_absolute_url())

      teammates=team.players.all().exclude(Q(slug=request.user.slug))
      invitations = Invitations.objects.filter(team=team).values('player')

      return render(request, self.template, self.get_user_context(
         title='Команда',
         mates=teammates,
         users=User.objects.all().exclude(Q(slug=request.user.slug) | Q(id__in=teammates) | Q(id__in=invitations))
      ))

   def post(self, request):
      data = request.POST
      team = request.user.team

      if (team.leader != request.user): 
         return HttpResponseRedirect(request.user.get_absolute_url())

      name = data.get('name', False)
      add_pls = data.get('invite', False)
      del_pls = data.get('delete', False)

      if name: 
         if Teams.objects.filter(name=name):
            return JsonResponse({'errors': {'name': 'Название занято'}})
         
         team.name = name
         team.save()
      
      if add_pls:
         players = User.objects.filter(pk__in=add_pls.split(','))
         for player in players:
            Invitations.objects.get_or_create(team=team, player=player)

      if del_pls:
         players = User.objects.filter(pk__in=del_pls.split(','))
         for player in players:
            player.team = None
            player.save()

      return JsonResponse({'succes': '500'})

# ПОКИНУТЬ КОМАНДУ
class LeaveTeamVeiw(LoginRequiredMixin, View):
   def get(self, request):
      user = request.user
      team = user.team

      if not team: return HttpResponseRedirect(reverse('about'))

      if team.leader == user: 
         team.delete()
      else:
         user.team = None
         user.save()
      
      return HttpResponseRedirect(user.get_absolute_url())

# УДАЛИТЬ КОМАНДУ
class DeleteTeamVeiw(LoginRequiredMixin, View):
   def get(self, request):
      user = request.user
      team = user.team

      if team is None or not self.is_ajax(): 
         return HttpResponseRedirect(reverse('about'))

      if team.leader == user: 
         team.delete()
      else:
         return HttpResponseRedirect(reverse('about'))
      
      return HttpResponseRedirect(user.get_absolute_url())

class AcceptInvitationView(LoginRequiredMixin, View):
   def post(self, request):
      user = request.user
      data = request.POST

      if ('invite_id' in data):
         invitation = get_object_or_404(Invitations, pk=data['invite_id'])

         if (invitation.team.players.count() < 4):
            request.user.team = invitation.team
            request.user.save()
            invitation.delete()
         else:
            pass
         
         return HttpResponse()

      else:
         return HttpResponseServerError()

class RejectInvitationView(LoginRequiredMixin, View):
   def post(self, request):
      user = request.user
      data = request.POST

      if ('invite_id' in data):
         invitation = get_object_or_404(Invitations, pk=data['invite_id'])
         invitation.delete()
         return HttpResponse()

      else:
         return HttpResponseServerError()










