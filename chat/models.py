from django.db import models
from PTD import settings

# Create your models here.
class Messages(models.Model):
   message = models.CharField(max_length=10000)
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   date_created = models.DateTimeField(auto_now_add=True, blank=True)

   class Meta:
      verbose_name = 'Сообщение'
      verbose_name_plural = 'Сообщения'
      ordering = ['date_created']
   
   def __str__(self):
      return self.message

   def get_date(self):
      hours = self.date_created.hour + 3
      str_date = ''

      if hours > 24:
         hours -= 24
      elif hours == 24:
         hours = 0

      if hours < 10:
         return f'0{hours}:{self.date_created.minute}'

      return f'{hours}:{self.date_created.minute}'


