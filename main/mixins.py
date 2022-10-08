from .models import *
from chat.models import *
from .forms import *
from PTD import settings
from django.core.cache import cache
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

            if self.request.user.is_authenticated:
                  print(self.request.user.is_online)
                  self.request.user.extend_online()
                  print(self.request.user.is_online)
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

            context['menu'] = user_menu

            context['aside_new'] = cache.get_or_set('aside_new', News.objects.filter(is_published=True).first(),  60 * 3)
            context['aside_tours'] = cache.get_or_set('aside_tours', Tournament.objects.all()[:5], 60 * 3)

            context['recaptcha_site_key'] = settings.RECAPTCHA_PUBLIC_KEY

            return context