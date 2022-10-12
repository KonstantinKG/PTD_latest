const chat_form = document.querySelector('.chat__form');
const chat_input = document.querySelector('.chat__input');
const chat_aside__form = document.querySelector('.chat-aside__form');
const chat_aaside_input = document.querySelector('.chat-aside__input');
const chat_body = document.querySelector('.chat__content')
const chat_aside_body = document.querySelector('.chat-aside__content')
const userNickname = JSON.parse(document.getElementById('json-username').textContent);
let is_scroll = true;

let link = 'ws://' + window.location.host + '/ws/' + 'chat/',
   timezoneOffset = new Date().getTimezoneOffset();

if (window.location.protocol == 'https:')
   link = 'wss://' + window.location.host + '/ws/' + 'chat/'
   
const chatSocket = new WebSocket(
   link
)

chatSocket.onmessage = function(e){
   const data = JSON.parse(e.data);

   if (data.message) {
      let html_photo, html_pos;

      if (data.photo) html_photo =  `<picture><source srcset="${data.photo}" type="image/webp"><img src="${data.photo}" alt=""></picture>`
      else html_photo = `<picture><source srcset="/static/main/img/header/profile.webp" type="image/webp"><img src="/static/main/img/header/profile.png" alt=""></picture>`

      if (data.pos_info[0]) html_pos = `style="color: ${data.pos_info[1]};">${data.pos_info[0]}`
      else html_pos = `style="color: grey;">Отсутсвует `

      let html;

      if (chat_body) {
         if (data.nickname == userNickname) {
            html = `
               <div class="chat__user chat__user_me send">
                  <div class="chat__user-msg">
                     <div class="chat__msg">
                        ${data.message}
                     </div>
                     <time class="chat__time">${data.date}</time>
                  </div>
               </div>
            `
         }
         else {
            html = 
            `
               <div class="chat__user send">
                  <div class="chat__user-data">
                     <a href="profile/${data.nickname}" class="chat__user-avatar">
                        ${html_photo}
                     </a>
                     <div class="chat__user-items">
                        <div class="chat__user-item chat__user-item_nickname">${data.nickname}</div>
                        <div class="chat__user-item chat__user-item_post" ${html_pos}</div>
                     </div>
                  </div>
                  <div class="chat__user-msg">
                     <div class="chat__msg">
                        ${data.message}
                     </div>
                     <time class="chat__time">${data.date}</time>
                  </div>
               </div>
            `
         }

         chat_body.insertAdjacentHTML('beforeend', html);
         if (is_scroll) scrollToBottom(chat_body);
      } 
      else if (chat_aside_body) {
         if (data.nickname == userNickname) {
            html = `
            <div class="chat-aside__user chat-aside__user_me send">
               <div class="chat-aside__user-msg">
                  <div class="chat-aside__msg">
                     ${data.message}
                  </div>
                  <time class="chat-aside__time">${data.date}</time>
               </div>
            </div>
            `
         }
         else {
            html = `
               <div class="chat-aside__user send">
                  <div class="chat-aside__user-data">
                     <a href="profile/${data.nickname}" class="chat-aside__user-avatar">
                        ${html_photo}
                     </a>
                     <div class="chat-aside__user-items">
                        <div class="chat-aside__user-item chat-aside__user-item_nickname">${data.nickname}</div>
                        <div class="chat-aside__user-item chat-aside__user-item_post"${html_pos}</div>
                     </div>
                  </div>
                  <div class="chat-aside__user-msg">
                     <div class="chat-aside__msg">
                        ${data.message}
                     </div>
                     <time class="chat-aside__time">${data.date}</time>
                  </div>
               </div>
            `
         }
         
         chat_aside_body.insertAdjacentHTML('beforeend', html);
         if (is_scroll) scrollToBottom(chat_aside_body);
      } 
   }
}

chatSocket.onclose = function(e){
   console.log('onclose');
}



function add_message_listener(form, input, ch_body)
{
   if (form) {
      ch_body.addEventListener('scroll', () => {is_scroll = false})
      form.addEventListener('submit', (e) => {
         e.preventDefault();
         
         if (userNickname && input.value)
         {
            const message = input.value
            

            chatSocket.send(JSON.stringify({
               'message': message,
               'nickname': userNickname
            }))

            is_scroll = true
            input.value = '';
         }

         return false;
      })
   }
}

chatSocket.onopen = function(e)
{
   add_message_listener(chat_form, chat_input, chat_body);
   add_message_listener(chat_aside__form, chat_aaside_input, chat_aside_body);
}


function scrollToBottom(item)
{
   item.scrollTop = item.scrollHeight;
}

// function add_message_listener(form, input)
// {
//    if (form) {
//       form.addEventListener('submit', (e) => {
//          e.preventDefault();

//          if (input.value.length > 0)
//          {
//             data = new FormData(form);
//             fetch('addmessage', {
//                method: 'POST',
//                // credentials: 'include',
//                body: JSON.stringify({
//                   "message": data.get("message")
//                }),
//                headers:{
//                   'Content-Type': 'application/x-www-form-urlencoded',
//                   'X-CSRFToken': getCookie('csrftoken'),
//                   'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
//                }
//             }).then(response => {
//                input.value = '';
//                console.log(response)
//             })
//          }
//       })
//    }
// }

// add_message_listener(chat_form, chat_input);
// add_message_listener(chat_aside__form, chat_aaside_input);


// function check_messages()
// {
//    fetch('/chat/check', {
//       method: 'GET'
//    }).then(response => response.json())
//       .then(data => JSON.parse(data.messages))
//          .then(info => {
            
//             let body;
//             if (chat_body) body = chat_body;
//             else if (chat_aside_body) body = chat_aside_body

//             body.innerHTML = ''

//             for (let index = 0; index < info.length; index++) {
//                const message = info[index]['fields'];
//                create_message(message, body)
//             }
//          })
// }

// setInterval(check_messages, 1000);

// function create_message(msg, body)
// {
//    comp_username = document.querySelector('.user__nickname').value

//    message = msg['message']
//    nickname = msg['username']
//    position = msg['position']
//    color = msg['pos_color']
//    photo = msg['photo'] 
   
//    console.log(position, typeof(position))

//    body.insertAdjacentHTML('beforeend', 
//       `
//       <div class="chat__user ${nickname === comp_username ? 'chat__user_me' : ''}">
//          <div class="chat__user-data">
//             <a href="" class="chat__user-avatar">
//                <picture><source srcset="${photo != null ? photo: "../main/static/main/img/header/profile.webp"}" type="image/webp"><img src="${photo != null ? photo: "../main/static/main/img/header/profile.webp" }" alt=""></picture>
//             </a>
//             <div class="chat__user-items">
//                <div class="chat__nickname">${nickname}</div>
//                <div class="chat__post" style="color:${color};">${position != null ? position : ''}</div>
//             </div>
//          </div>
//          <div class="chat__user-msg">
//             <div class="chat__msg">
//                ${message}
//             </div>
//          </div>
//       </div>
//       `
//    )

// }

// function getCookie(name) {
//    let cookieValue = null;
//    if (document.cookie && document.cookie !== '') {
//       const cookies = document.cookie.split(';');
//       for (let i = 0; i < cookies.length; i++) {
//          const cookie = cookies[i].trim();
//            // Does this cookie string begin with the name we want?
//          if (cookie.substring(0, name.length + 1) === (name + '=')) {
//             cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//             break;
//          }
//       }
//    }
//    return cookieValue;
// }