import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTD.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application

from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
   "http": get_asgi_application(),
   "websocket": AuthMiddlewareStack(
      URLRouter(
         websocket_urlpatterns
      )
   )
   ## IMPORTANT::Just HTTP for now. (We can add other protocols later.)
})