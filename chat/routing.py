from django.urls import path, re_path

from .consumers import *


websocket_urlpatterns = [
   path('ws/chat/', ChatConsumer.as_asgi()),
   re_path(r'^ws/\s*$|/\w+$', ChatConsumer.as_asgi()),
]