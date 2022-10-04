// FETCH для формы авторизации
const loginForm = document.querySelector('.login__form')

if (loginForm) {
   loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      createFetchRequest(
         form=loginForm,
         func=successLogin
      )
   })
}

function successLogin() {
   document.location.reload();
}

// FETCH для формы регистрации
const registerForm = document.querySelector('.register__form')

if (registerForm) {
   registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      createFetchRequest(
         form=registerForm,
         func=successRegister
      )
   })
}

function successRegister() {
   // Тут должен открыватья поп ап с уведомлением что письмо было отправленно (ПОП АП ДЛЯ ПОДТВЕРЖДЕНИЯ)
   alert('Вам отправили письмо')
}

// FETCH для формы восстановления пароля (отправка сообщения на почту)
const resetEmailForm = document.querySelector('.reset-email__form')


if (resetEmailForm) {
   resetEmailForm.addEventListener('submit', (e) => {
      e.preventDefault();
      createFetchRequest(
         form=resetEmailForm,
         func=successResetEmail
      )
   })
}

function successResetEmail() {
   // Тут должен открыватья поп ап с уведомлением что письмо было отправленно (ПОП АП ДЛЯ ВОССТАНОВЛЕНИЯ)
}

// FETCH для формы восстановления пароля (ввод нового пароля)

const newPassForm = document.querySelector('.new-password__form')

if (newPassForm) {
   newPassForm.addEventListener('submit', (e) => {
      e.preventDefault();
      createFetchRequest(
         form=newPassForm,
         func=successNewPassword
      )
   })
}

function successNewPassword() {
   // Тут должен открыватья поп ап с логином или уведомление поп ап о успешной смене пароля
}

function createFetchRequest(form, func)
{
   let url = form.getAttribute('action');
   let formData = new FormData(form);
   let data = prepareData(formData);

   let popup = form.closest('.popup');

   if (popup) popup.classList.add('_sending');

   fetch(url,
   {
      method: "POST",
      credentials: "same-origin",
      headers: {
         "X-Requested-With": "XMLHttpRequest",
         "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(data)
   })
   .then(response => {
      if (popup) popup.classList.remove('_sending');

      if (response.ok) return response.json()
      else {
         displayErrors(form, {'server': '500'});
         return false;
      }
   })
   .then(data => {
      if (data) {
         if ('errors' in data) displayErrors(form, data['errors'])
         else func();
      }
   })
}

function prepareData(data)
{  
   let temp = {}

   for (let key of data.keys()) {
      temp[key] = data.get(key)
   }
   return temp;
}

function displayErrors(form, errors)
{
   const formInputs = form.querySelectorAll('input')
   const commonErrorsField = form.querySelector('.popup__error')

   formInputs.forEach(input => {
      if (input.name in errors)
      {
         input.setAttribute('placeholder', errors[input.name])
         input.classList.add('_error');
         input.value = ''
      }
   });

   if ('__all__' in errors) commonErrorsField.innerText = errors['__all__'];
   else if ('server' in errors) commonErrorsField.innerText = 'На сервере произошла ошибка. Попробуйте отправить форму еще раз';
   else if ('email_failed' in errors) commonErrorsField.innerText = errors['email_failed']
}

function getCookie(name) {
   let cookieValue = null;
   if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
         const cookie = cookies[i].trim();
           // Does this cookie string begin with the name we want?
         if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
         }
      }
   }
   return cookieValue;
}