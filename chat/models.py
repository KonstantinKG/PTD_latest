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
