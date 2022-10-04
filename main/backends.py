from .models import User
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q

class AuthBackend(BaseBackend):
   supports_object_permissions = True
   supports_anonymous_user = False
   supports_inactive_user = False

   def get_user(self, user_id):
      try:
         return User.objects.get(pk=user_id)
      except User.DoesNotExist:
         return None

   def authenticate(self, request, username, password):
      try:
         user = User.objects.get(
            Q(nickname=username) | Q(email=username) | Q(telephone=username)
         )
      except User.DoesNotExist:
         return None

      return user if user.check_password(password) else None