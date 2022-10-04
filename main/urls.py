from django.urls import path

from .views import *

urlpatterns = [
   path('', AboutView.as_view(), name='about'),
   path('members', MembersView.as_view(), name='members'),
   path('news', NewsView.as_view(), name='news'),
   path('news/<slug:new_slug>', SingleNewView.as_view(), name='new'),
   path('profile/<slug:user_slug>', ProfileView.as_view(), name='profile'),
   path('profile/<slug:user_slug>/edit', EditProfileView.as_view(), name='profile_edit'),
   path('team/create', CreateTeamView.as_view(), name='create_team'),
   path('team/leave', LeaveTeamVeiw.as_view(), name='leave_team'),
   path('team/edit', editTeamView.as_view(), name='edit_team'),
   path('team/delete', DeleteTeamVeiw.as_view(), name='delete_team'),
   path('invite/accept', AcceptInvitationView.as_view(), name='accept_invite'),
   path('invite/delete', RejectInvitationView.as_view(), name='reject_invite'),
]