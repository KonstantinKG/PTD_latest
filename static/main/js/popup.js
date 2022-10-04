// const popup_forms = document.querySelectorAll('.popup form')


// function add_form_listener(form, action)
// {
//    if (form) {
//       form.addEventListener('submit', (e) => {
//          e.preventDefault();

//          data = prepare_data(form)
//          fetch(action, {
//             method: 'POST',
//             // credentials: 'include',
//             body: JSON.stringify(data),
//             headers:{
//                'Content-Type': 'application/x-www-form-urlencoded',
//                'X-CSRFToken': getCookie('csrftoken'),
//                'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
//             }
//          }).then(response => response.json())

//       })
//    }
// }

// if (popup_forms.length > 0)
// {
//    for (let i = 0; i<popup_forms.length; i++)
//    {
//       const form = popup_forms[i]
//       const action = form.getAttribute('action');
//       add_form_listener(form, action);
//    }
// }

// // function check_messages()
// // {
// //    fetch('/chat/check', {
// //       method: 'GET'
// //    }).then(response => response.json())
// //       .then(data => JSON.parse(data.messages))
// //          .then(info => {
            
// //             let body;
// //             if (chat_body) body = chat_body;
// //             else if (chat_aside_body) body = chat_aside_body

// //             body.innerHTML = ''

// //             for (let index = 0; index < info.length; index++) {
// //                const message = info[index]['fields'];
// //                create_message(message, body)
// //             }
// //          })
// // }

// // setInterval(check_messages, 1000);
// function prepare_data(form)
// {
//    let inputs = form.querySelectorAll('input');
//    let data = {}

//    for (let index = 0; index < inputs.length; index++) {
//       const input = inputs[index];
//       const value = input.value
//       const name = input.name

//       data[name] = value
//    }
//    console.log(data)

//    return data;
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