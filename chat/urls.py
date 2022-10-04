from django.urls import path

from .views import *

urlpatterns = [
   path('', ChatView.as_view(), name='chat'),
]