from .models import *
from django import forms

class MessageForm(forms.ModelForm):
   message = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "chat__input", 'placeholder': 'Сообщение...'}))

   class Meta:
      model = Messages
      fields = ['message',]
      