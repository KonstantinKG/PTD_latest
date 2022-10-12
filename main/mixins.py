from .models import *
from chat.models import *
from .forms import *
from PTD import settings
from tournaments.models import Tournament

menu = [
      {'title': "О клане", 'url_name': 'about', 'current': ''},
      {'title': "Состав", 'url_name': 'members', 'current': ''},
      {'title': "Новости", 'url_name': 'news', 'current': ''},
      {'title': "Турниры", 'url_name': 'tours', 'current': ''},
]

class DataMixin:

      def get_user_context(self, **kwargs):
            context = kwargs

            self.request.session['last_visited_page'] = self.request.path_info

            if self.request.user.is_authenticated:
                  self.request.user.extend_online()
                  context['messages'] = Messages.objects.all().select_related('user', 'user__position')

            user_menu = menu.copy()

            cur_url = ''
            if 'curr_page_url' in kwargs:
                  cur_url = kwargs['curr_page_url']

            for item in user_menu:
                  if item['url_name'] == cur_url:
                        item['current'] = 'active'
                  else:
                        item['current'] = ''

            if self.request.session.get('confirmed_user'):
                  context['confirmed_user'] = True
                  self.request.session['confirmed_user'] = False

            if self.request.session.get('reset_confirmed'):
                  context['reset_confirmed'] = True
                  self.request.session['reset_confirmed'] = False

            context['menu'] = user_menu

            context['aside_new'] = News.objects.filter(is_published=True).first()
            context['aside_tours'] = Tournament.objects.all()[:5]

            context['recaptcha_site_key'] = settings.RECAPTCHA_PUBLIC_KEY

            return context