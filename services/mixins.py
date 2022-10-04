from PTD import settings
import smtplib
import requests
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponseServerError

class ServiceMixin:

   def get(self, request):
      return HttpResponseServerError()

   def is_ajax(self, request):
      is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

      if not is_ajax:
         return HttpResponseServerError()
      return True

   def check_timers(self, request, try_name, timer_name, timer_secs=300, tries_amount=6):
      tries = request.session.get(try_name, -1)
      timer = request.session.get(timer_name, False)

      if (tries < 0 or not timer):
         tries = tries_amount
         timer = self._date_to_string(datetime.now())
         request.session[try_name] = tries
         request.session[timer_name] = timer

      elif (tries <= 0): 
         return JsonResponse({'resend': {
            'tries': tries,
            'timer': self._count_secs_left(timer, timer_secs),
            'error': 'Вы привысили лимит ошибок попробуйте через 3 часа'
         }})

      elif ((datetime.now() - self._string_to_date(timer)).seconds < timer_secs):
         return JsonResponse({'resend': {
            'tries': tries,
            'timer': self._count_secs_left(timer, timer_secs),
            'error': 'Отправка сообщения будет доступна по истечению таймера'
         }})
      else:
         timer = self._date_to_string(datetime.now())
         request.session[timer_name] = timer

      return self._count_secs_left(timer, timer_secs)

   def _date_to_string(self, date): 
      return date.strftime('%d.%m.%Y %H:%M:%S')

   def _string_to_date(self, string): 
      return datetime.strptime(string, '%d.%m.%Y %H:%M:%S')
   
   def _count_secs_left(self, timer, secs):
      print((datetime.now() - self._string_to_date(timer)).seconds, (datetime.now() - self._string_to_date(timer)))
      return secs - ((datetime.now() - self._string_to_date(timer)).seconds)
      

class EmailSender:
   def send_mail(
      self,
      subject_template_name,
      email_template_name,
      context,
      from_email,
      to_email,
   ):
      """
      Send a django.core.mail.EmailMultiAlternatives to `to_email`.
      """
      subject = loader.render_to_string(subject_template_name, context)
      # Email subject *must not* contain newlines
      subject = "".join(subject.splitlines())
      body = ''

      email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
      if email_template_name:
         html_email = loader.get_template(email_template_name).render(context)
         email_message.attach_alternative(html_email, "text/html")

      email_message.send()

   def create_mail(
      self,
      tries_name,
      timer,
      domain_override=None,
      use_https=False,
      from_email=settings.EMAIL_HOST_USER,
      request=None,
      extra_email_context=None,
      user = None,
      reset_email = False,
      confirm_email = False,
      token_generator=default_token_generator,
   ):
      print(timer, 'TIMER_____TIMER')
      if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
      else:
         site_name = domain = domain_override

      user_email = user.email
      context = {
         "email": user_email,
         'from_email': from_email,
         'year': datetime.now().year,
         "site_name": site_name,
         'domain': domain,
         "user": user,
         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
         "protocol": "https" if use_https else "http",
             **(extra_email_context or {}),
      }

      if confirm_email:
         subject_template_name="registration/confirm_user_subject.txt"
         email_template_name="registration/confirm_user_email.html"

         token = token_generator.make_token(user)
         request.session['confirm_token'] = token

         context.update({
            "token": token
         }) 

      if reset_email:
         subject_template_name="registration/password_reset_subject.txt"
         email_template_name="registration/password_reset_email.html"

         token = token_generator.make_token(user)
         request.session['reset_token'] = token

         context.update({
            "token": token
         }) 

      try:
         request.session['email'] = user_email
         self.send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            user_email,
         )

      except smtplib.SMTPDataError:
         user.delete()
         return JsonResponse({'errors': {'email': 'Введенная почта не существует'}})

      except Exception:
         return JsonResponse({
            'errors': {'email_failed': 'При отправке сообщения произошла ошибка попробуйте отправить сообщение повторно'}
         })

      else:
         tries = request.session[tries_name] - 1
         request.session[tries_name] = tries

         return JsonResponse({'resend': {
            'tries': tries,
            'timer': timer,
            'error': ''
         }})