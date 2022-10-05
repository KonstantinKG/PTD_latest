from .forms import *
from .models import Messages
from PTD import settings
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
# Create your views here.
def tours(request):
   pass

class ChatView(ListView):
   model = Messages
   template_name = 'chat/chat.html'
   context_object_name = 'messages'

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)

      context['prev_page'] = self.request.session['last_visited_page']
      context['recaptcha_site_key'] = settings.RECAPTCHA_PUBLIC_KEY
      context['form'] = MessageForm()

      return context
   
   def get_queryset(self):
      return super().get_queryset().select_related('user', 'user__position')

   def get(self, request):
      if not request.user.is_authenticated:
         return PermissionDenied()

      super().get(request)

