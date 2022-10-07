from django.urls import path
from django.contrib.auth.views import PasswordResetConfirmView

from .views import *

urlpatterns = [
   # Recaptcha handler
   path('recaptcha', recaptcha, name='recaptcha'),

   # Privacy Policy
   path('privacy', PrivacyView.as_view(), name='privacy'),

   # Cookie Policy
   path('cookie', CookieView.as_view(), name='cookie'),

   # Admin custom behavior for tournament model
   path('admin/getteams', getTeams, name='get_teams'),
   path('admin/getteam', getTeam, name='get_team'),
   path('admin/teams/edit/<slug:slug>', EditTourTeamsView.as_view(), name='edit_teams'),
   path('admin/teams/delete/<slug:slug>', DeleteTourTeamsView.as_view(), name='delete_teams'),

   # Login Register
   path('login', LoginView.as_view(), name='login'),
   path('register', RegisterView.as_view(), name='register'),
   path('logout', logout_user, name='logout'),

   # Password Recovery
   path('recovery/email', ResetEmailView.as_view(), name='recovery'),
   path('recovery/<uidb64>/<token>', UserRecoveryConfirmView.as_view(), name='recovery_confirm'),
   # path('recovery/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='recovery_confirm'),
   path('recovery/reset', UserRecoveryResetView.as_view(), name='recovery_reset'),

   # User Activation
   path('confirm/<uidb64>/<token>', UserConfirmView.as_view(), name='user_confirm'),
   
   # Resend Emails (Recovery and Confirmation)
   path('resend/confirm', ResendConfirmEmailView.as_view(), name='resend_confirm_email'),
   path('resend/recovery', ResendRecoveryEmailView.as_view(), name='resend_recovery_email'),
]