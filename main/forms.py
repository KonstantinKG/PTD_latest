from .models import *
from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

UserModel = get_user_model()

class RegistrationForm(UserCreationForm):

   nickname = forms.CharField(label='Ник', widget=forms.TextInput(attrs={'class': 'popup__input'}))
   email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'popup__input'}))
   uid = forms.CharField(label='UID',validators=[RegexValidator("^[0-9]{19}$", 'Некоректный UID. Длина 19 цифр')], widget=forms.TextInput(attrs={'class': 'popup__input'}))
   password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'popup__input'}))
   password2 = forms.CharField(label='Повтор', widget=forms.PasswordInput(attrs={'class': 'popup__input'}))

   class Meta:
      model = User
      fields = ('nickname', 'email', 'uid', 'password1', 'password2')

class LoginForm(AuthenticationForm):

   username = forms.CharField(widget=forms.TextInput(attrs={'class': 'popup__input', 'placeholder': 'Никнейм, E-mail, Телефон'}))
   password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'popup__input'}))
   remember_me = forms.BooleanField(label='Запомнить', widget=forms.CheckboxInput(attrs={'class': 'popup__input-checkbox'}), required=False)

class EditForm(ModelForm):
   class Meta:
      model = User
      fields = ['nickname','name', 'about', 'photo', 'email','telephone', 'instagram', 'telegram', 'vkontakte']

class ResetPasswordEmailForm(forms.Form):
   email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'popup__input', 'placeholder': 'E-mail'}))

   def user_exists(self, email):
      users = self.get_users(email)

      if len(users) <= 0 :
         self.add_error('email', 'Пользователя с таким емайлом не существует')
         return False

      return users[0]

   def get_users(self, email):
      email_field_name = UserModel.get_email_field_name()
      users = UserModel._default_manager.filter(
         **{
            "%s__iexact" % email_field_name: email,
         }
      )
      
      return users

class ResetPasswordCodeForm(forms.Form):
   code = forms.CharField(widget=forms.TextInput(attrs={'class': 'popup__input', 'placeholder': 'Код восстановления'}), validators=[RegexValidator("^[0-9]{6}$", 'Неправильный формат кода восстановления')])

   def is_code_match(self, request, code):
      request_code = request.session['code']
      tries = int(request.session['tries'])

      if code != request_code:
         request.session['tries'] = str(tries-1)
         self.add_error("code", 'Неверный код')
         return False
      return True

   def have_tries(self, tries):
      if tries == '0':
         self.add_error('code', 'Вы привысили лимит попыток аккаунт будет заблокирован на 3 часа')
   
   def get_user(self, email):
      return UserModel.objects.get(email=email)



