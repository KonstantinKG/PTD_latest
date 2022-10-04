from django.urls import path

from .views import *

urlpatterns = [
   path('', TournamentView.as_view(), name='tours'),
   path('<slug:tour_slug>', SingleTournamentView.as_view(), name='tour'),
   path('<slug:tour_slug>/table', SaveTourTable.as_view(), name='table'),
]