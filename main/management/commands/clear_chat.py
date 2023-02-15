
from PTD import settings
from django.core.management.base import BaseCommand
from chat.models import Messages

class ClearChatCommand(BaseCommand):
   help = 'Чистит чат'

   def handle(self, *args, **kwargs):
      Messages.objects.all().delete()
