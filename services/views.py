import json
import requests
from PTD import settings
from main.forms import *
from main.models import User, TeamParticapation, Teams
from tournaments.models import Tournament
from .mixins import *
from main.mixins import *
from django.shortcuts import render
from django.contrib.auth import logout, login
from django.urls import reverse
from django.db.models import Q, Count
from django.views.generic import View
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse, JsonResponse, HttpResponseServerError, HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.views.generic import View

UserModel = get_user_model()


# Processing RECAPTCHA 
def recaptcha(request):
   if request.method == 'POST':
      data = json.load(request)

      if ('token' in data):
         data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': data['token']
         }
         r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
         result = r.json()

         request.session['recaptcha_checked'] = True

         if result['score'] < 0.5:
            pass

         return HttpResponse('ReCaptcha recevied')
      
      return HttpResponse('ReCaptcha token lost')

   return HttpResponse('This URL does not support GET requests')

# Privacy policy
class PrivacyView(View, DataMixin):
   template = 'service/privacy.html'

   def get(self, request):
      return render(request, self.template, self.get_user_context(
         title='Политика конфиденциальности'
      ))

# Cookie policy
class CookieView(View, DataMixin):
   template = 'service/cookie.html'

   def get(self, request):
      return render(request, self.template, self.get_user_context(
         title='Политика cookie'
      ))

# Getting TEAMS for admin Tournaments
def getTeams(request):
   if request.method == 'POST':
      if ('tournament' in request.POST and request.POST.get('tournament') != ''):
         teams = list(TeamParticapation.objects.filter(tournament__slug=request.POST['tournament']).values('team__name'))

         return JsonResponse({'teams': teams})
      else:
         return HttpResponseServerError()

   return HttpResponse('This URL does not support GET requests')

# Getting TEAM for admin Tournament
def getTeam(request):
   if request.method == 'POST':
      if ('tournament' in request.POST and 'team' in request.POST):
         # Игроки состоящие в команде
         team_users = Teams.objects.filter(pk=request.POST['team'])

         # Игроки играющие за эту команду на турнире
         team_users_play = TeamParticapation.objects.filter(team__id=request.POST['team'], tournament__slug=request.POST['tournament'])

         team_users = list(team_users.values('players', 'players__nickname'))
         team_users_play = list(team_users_play.values('particapants', 'particapants__nickname'))

         return JsonResponse({
            'team_users': team_users,
            'team_users_play': team_users_play
         })
      else:
         return HttpResponseServerError()

   return HttpResponse('This URL does not support GET requests')

# Добавление и Редактирование Участвующих команд на турнире в админке
class EditTourTeamsView(View):
   def post(self, request, slug):
      tournament = Tournament.objects.get(slug=slug)
      tour_typo = int(tournament.typo)

      if request.POST['players'] != '':
         # получаем список ID игроков
         players = request.POST['players'].split(',')
         pls_len = len(players)
         
         # Если кол-во учавствующих за команду игроков равно кол-ву игроков в команде турнира
         if (pls_len) == tour_typo:
            team = Teams.objects.get(pk=int(request.POST['team']))

            # Получаем запись из модели хранящей (команду, турнир и игроков играющих за команду на турнире)
            team_party = TeamParticapation.objects.get_or_create(tournament=tournament, team=team)[0]

            exist_players = team_party.particapants.values('id')
            for value in players:
               # Если игрок не записан на турнир добавляем
               if (value not in exist_players):
                  player = User.objects.get(id=value)

                  team_party.particapants.add(player)
            
            return JsonResponse({'success': 'Команда успешно добавлена на турнир'})

         elif (pls_len) > tour_typo:
            team_party.delete()
            return JsonResponse({'error': f'Вы выбрали больше игроков ({pls_len}) чем может учавствовать на турнире ({tour_typo})'})
         else:
            team_party.delete()
            return JsonResponse({'error': f'Вы выбрали меньше игроков ({pls_len}) чем может учавствовать на турнире ({tour_typo})'})
      else:
         return JsonResponse({'error': f'Вы не выбрали ни одного игрока! Необходимо: {tour_typo}. Для удаления команды перейдите по кнопке для удаления турнира на странице этого турнира'})
      
   def get(self, request, slug):
      tour = Tournament.objects.get(slug=slug)

      # Берем только те команду у которых достаточно игроков для участия на турнире
      teams = Teams.objects.annotate(num_players = Count('players')).filter(num_players__gte=tour.typo)
      
      return render(request, 'admin/tournament_edit_team.html', {
         "teams": teams,
         "tour": tour
      })

# Удалене команд с турнира в админке
class DeleteTourTeamsView(View):
   def post(self, request, slug):
      if request.POST['teams'] != '':
         teams = Tournament.objects.get(slug=slug).particapants.filter(team__id__in=request.POST['teams'].split(','))

         for team in teams:
            team.delete()

         return JsonResponse({'success': 'Команды успешно удалены с турнира'})
      else:
         return JsonResponse({'error': 'Вы не выбрали ни одной команды!'})

   def get(self, request, slug):
      tour = Tournament.objects.get(slug=slug)

      # Все команды зарегестрированные на турнире
      teams_party = tour.particapants.all().select_related('team')
      
      return render(request, 'admin/tournament_delete_team.html', {
         "teams_party": teams_party,
         "tour": tour
      })

# AUTHORITHATION
class LoginView(View, ServiceMixin):
   def post(self, request):
      data = json.load(request)
      form = LoginForm(data=data)

      if form.is_valid() and self.is_ajax(request):
         user = form.get_user()

         conf_user = request.session.get('confirmed_user', False)
         if conf_user: del request.session['confirmed_user']

         cleaned = form.cleaned_data

         if not cleaned.get('remember_me'): request.session.set_expiry(0)
         else: request.session.set_expiry(14 * 24 * 60 * 60)

         login(request, user, backend='main.backends.AuthBackend')

         return JsonResponse({'success': True})

      elif form.get_user() and not form.get_user().is_active: 
         request.session['email'] = form.get_user().email

         return JsonResponse({'errors': form.errors})

      return JsonResponse({'errors': form.errors})

def logout_user(request):
   logout(request)
   return HttpResponseRedirect(reverse('about'))

# REGISTRATION
class RegisterView(View, ServiceMixin, EmailSender):
   def post(self, request):
      data = json.load(request)
      form = RegistrationForm(data=data)

      if request.session.get('registered'):
         return JsonResponse({'errors': {'__all__': ['Вы уже регистрировали аккаунт сегодня']}})

      if form.is_valid() and self.is_ajax(request):

         email = form.cleaned_data.get('email')
         username = form.cleaned_data.get('nickname')

         request.session['registered'] = True

         user = form.save()

         timer = self.check_timers(request, 'confirm_try', 'confirm_timer', timer_secs=300)

         if not isinstance(timer, int): return timer 

         return self.create_mail(
            tries_name="confirm_try",
            timer=timer,
            user=user,
            request=request,
            confirm_email=True
         )
      
      return JsonResponse({'errors': form.errors})


# Password Recovery View
class ResetEmailView(View, EmailSender, ServiceMixin):
   def post(self, request):
      data = json.load(request)
      email = data['email']
      form = ResetPasswordEmailForm(data=data)

      user = form.user_exists(email)

      if form.is_valid() and self.is_ajax(request):

         timer = self.check_timers(request, 'reset_try', 'reset_timer', timer_secs=300)

         if not isinstance(timer, int): return timer 

         return self.create_mail(
            tries_name="reset_try",
            timer=timer,
            user=user,
            request=request,
            reset_email=True
         )

      return JsonResponse({'errors': form.errors})

# Password Recovery Confirmation View

INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"

class UserRecoveryConfirmView(View):
   reset_url_token = "set-password"
   token_generator = default_token_generator

   def get(self, request, uidb64, token):

      self.user = self.get_user(uidb64)

      if self.user is not None:

         if token == self.reset_url_token:
            session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
            if self.token_generator.check_token(self.user, session_token):

               request.session['reset_confirmed'] = True
               request.session['uid'] = uidb64

               last_page_url = request.session.get('last_visited_page', False)

               if last_page_url:
                  return HttpResponseRedirect(request.session['last_visited_page'])
               else:
                  return HttpResponseRedirect(reverse('about'))
                  
         else:
            if self.token_generator.check_token(self.user, token):

               self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
               redirect_url = self.request.path.replace(
                  token, self.reset_url_token
               )
               return HttpResponseRedirect(redirect_url)

      return HttpResponseRedirect(reverse('about'))

   def post(self, request):
      code_post = request.POST.get('code', False)
      code_tries = request.session.get('code_tries', False)

      if code_post:
         uidb64 = request.session.get(str(code_post), False)

         if code_tries <= 0:
            return JsonResponse({'errors': {'__all__': ['Попытки на ввод кода закончились. Отправьте письмо повторно']}})

         request.session['code_tries'] = code_tries - 1

         if uidb64 != False:
            request.session['reset_confirmed'] = True
            request.session['uid'] = uidb64

            last_page_url = request.session.get('last_visited_page', False)

            return JsonResponse({'succes': True})

         else:
            return JsonResponse({'errors': {'__all__': ['Неверный код']}})
      else:
         return HttpResponseRedirect(reverse('about'))
         

   def get_user(self, uidb64):
      try:
         uid = urlsafe_base64_decode(uidb64).decode()
         user = UserModel._default_manager.get(pk=uid)
      except (
         TypeError,
         ValueError,
         OverflowError,
         UserModel.DoesNotExist,
         ValidationError,
      ):
         user = None
      return user

# Password Recovery Reset View
class UserRecoveryResetView(View, ServiceMixin):
   def post(self, request):
      uidb64 = request.session.get('uid', False)
      if uidb64:
         user_id = urlsafe_base64_decode(uidb64).decode()
         user = UserModel.objects.get(pk=user_id)
      else:
         return HttpResponseRedirect(reverse('about'))
      
      data = json.load(request)
      form = SetPasswordForm(user=user, data=data)

      if form.is_valid() and self.is_ajax(request):
         del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
         del self.request.session['uid']
         del self.request.session['reset_confirmed']

         form.save()

         return JsonResponse({'success': True})
      
      return JsonResponse({'errors': form.errors})


# Resend Password Recovery Email View
class ResendRecoveryEmailView(View, ServiceMixin, EmailSender):
   def post(self, request):
      if self.is_ajax(request):
         data = json.load(request)

         if 'email' in request.session: 
            email = request.session['email']
         
         else: 
            return JsonResponse({'errors': {'__all__': 'Ваша почта была утерена пройдите форму восстановления пароля повторно'}})
         
         user = User.objects.get(Q(email=email) | Q(nickname=email) | Q(telephone=email))

         timer = self.check_timers(request, 'reset_try', 'reset_timer', timer_secs=300)

         if not isinstance(timer, int): return timer 

         return self.create_mail(
            tries_name="reset_try",
            timer=timer,
            user=user,
            request=request,
            reset_email=True
         )

      return HttpResponseRedirect(reverse('about'))


# User Confirmation View
class UserConfirmView(View):
   reset_url_token = "set-password"
   token_generator = default_token_generator

   def get(self, request, uidb64, token):

      self.user = self.get_user(uidb64)

      if self.user is not None:

         if token == self.reset_url_token:
            session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
            if self.token_generator.check_token(self.user, session_token):

               request.session['confirmed_user'] = True

               self.user.is_active = True
               self.user.save()

               last_page_url = request.session.get('last_visited_page', False)

               if last_page_url:
                  return HttpResponseRedirect(request.session['last_visited_page'])
               else:
                  return HttpResponseRedirect(reverse('about'))
                  
         else:
            if self.token_generator.check_token(self.user, token):

               self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
               redirect_url = self.request.path.replace(
                  token, self.reset_url_token
               )
               return HttpResponseRedirect(redirect_url)

   def post(self, request):
      code_post = request.POST.get('code', False)
      code_tries = request.session.get('code_tries', False)

      if code_post:
         uidb64 = request.session.get(str(code_post), False)
         self.user = self.get_user(uidb64)

         if code_tries <= 0:
            return JsonResponse({'errors': {'__all__': ['Попытки на ввод кода закончились. Отправьте письмо повторно']}})

         request.session['code_tries'] = code_tries - 1

         if uidb64 != False and self.user:
            request.session['reset_confirmed'] = True
            request.session['uid'] = uidb64

            self.user.is_active = True
            self.user.save()

            return JsonResponse({'succes': True})

         else:
            return JsonResponse({'errors': {'__all__': ['Неверный код']}})

      return HttpResponseRedirect(reverse('about'))

   def get_user(self, uidb64):
      try:
         # urlsafe_base64_decode() decodes to bytestring
         uid = urlsafe_base64_decode(uidb64).decode()
         user = UserModel._default_manager.get(pk=uid)
      except (
         TypeError,
         ValueError,
         OverflowError,
         UserModel.DoesNotExist,
         ValidationError,
      ):
         user = None
      return user

# Resend Confirm Email View
class ResendConfirmEmailView(View, ServiceMixin, EmailSender):
   def post(self, request):
      if self.is_ajax(request):
         data = json.load(request)

         if 'email' in request.session: 
            email = request.session['email']

         elif 'email' in data: 
            email = data['email']  
         
         else: 
            return JsonResponse({'errors': {'__all__': 'Не получилось установить вашу почту'}})

         timer = self.check_timers(request, 'confirm_try', 'confirm_timer', timer_secs=300)

         if not isinstance(timer, int): return timer 

         user = User.objects.get(Q(email=email) | Q(nickname=email) | Q(telephone=email))
         return self.create_mail(
            tries_name="confirm_try",
            timer=timer,
            user=user,
            request=request,
            confirm_email=True
         )

      return HttpResponseRedirect(reverse('about'))


def handler403(request, exception=None):
   return render(request, 'service/error403.html', {
      'title': '403'
   })

def handler404(request, exception=None):
   return render(request, 'service/error404.html', {
      'title': '404'
   })
