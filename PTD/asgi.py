import os
import django

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTD.settings')
django.setup()

application = ProtocolTypeRouter({
   "http": get_asgi_application(),
   "websocket": AuthMiddlewareStack(
      URLRouter(
         websocket_urlpatterns
      )
   )
   ## IMPORTANT::Just HTTP for now. (We can add other protocols later.)
})