const recaptchaKey = document.querySelector('.recaptcha_site_key').value;
console.log(recaptchaKey);

function getCSRF_TOKEN() {
   return document.querySelector('input[name="csrfmiddlewaretoken"]').value
}

if (recaptchaKey != '') {
   grecaptcha.ready(function() {
      grecaptcha.execute(recaptchaKey, {action: 'submit'}).then(function(token) {
         csrf = getCSRF_TOKEN()
   
         if (csrf) {
            fetch("../service/recaptcha", {
               method: "POST",
               credentials: "same-origin",
               headers: {
                  "X-Requested-With": "XMLHttpRequest",
                  "X-CSRFToken": csrf,
               },
               body: JSON.stringify(
                  {
                     "token": token
                  }
               )
            })
            .then(response => {
               if (response.ok) console.log('Recaptcha verified')
               else console.log('Server error')
            })
         }
      });
   });
}
