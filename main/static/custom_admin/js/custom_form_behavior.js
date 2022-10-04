document.addEventListener("DOMContentLoaded", () => {
   let TournamentForm = document.querySelector('#tournament_form');
   console.log("fasfasf", TournamentForm);
   if (TournamentForm) {
      let TournamentTypo = TournamentForm.querySelector('select[name="typo"]').value;

      if (TournamentTypo != "" && TournamentTypo != 1) {
         let futureTeams = TournamentForm.querySelector('.field-players'),
            tourSlug = TournamentForm.querySelector('input[name="slug"]').value;

         reformPlayersField(futureTeams, tourSlug, TournamentForm.csrfmiddlewaretoken.value);

         let fieldset = TournamentForm.querySelectorAll('fieldset'),
            customEditPanel;
         
         fieldset = fieldset[fieldset.length-1]

         customEditPanel = document.createElement('div');
         customEditPanel.classList.add('submit-row')
         customEditPanel.innerHTML = `
            <input type="button" onclick='gotoEditTablePage("${tourSlug}");' value="Турнирная таблица">
            <input type="button" onclick='gotoEditTeamPage("${tourSlug}");' value="Добавить/Редактиовать команды">
            <input type="button" onclick='gotoDeleteTeamPage("${tourSlug}")' value="Удалить команды">
         `
         console.log('asfasfsafsa', fieldset)
         fieldset.after(customEditPanel);
      }
   }   


   let teamEditSelect = document.querySelector('.custom-team__select');

   if (teamEditSelect) {
      teamEditSelect.addEventListener('input', e => {
         if (e.target.value != '') {
            let form = document.querySelector('.custom-team__edit-form'),
               data = new FormData(form),
               url = form.querySelector('input[name="get_team_url"]').value;

            fetch(url,
               {
                  method: "POST",
                  body: data
               })
               .then(response => {
                  if (response.redirected) return false;
         
                  if (response.ok) return response.json()
               })
               .then(data => {
                  if (!data) return;
                  console.log(data)
                  initEditTeamSelect(data);
            })
            
            form.addEventListener('submit', (e) => {
               e.preventDefault();

               if(e.keyCode !== 13){
                  sendTeamSelect(form, form.querySelector('#id_particapants_to'));
               }   
            })
         }

      })
   }

   let deleteForm = document.querySelector('.custom-team__delete-form');

   if (deleteForm) {
      let playingTeamsSelect = deleteForm.querySelector('#id_particapants_from'),
         deleteTeamsSelect = deleteForm.querySelector('#id_particapants_to');

      addTeamSelectFunctionallity(deleteForm, playingTeamsSelect, deleteTeamsSelect);

      deleteForm.addEventListener('submit', (e) => {
         e.preventDefault();

         if (e.keyCode !== 13) {
            let data = new FormData(deleteForm),
               options = deleteTeamsSelect.querySelectorAll('option'),
               errornote = deleteForm.querySelector('.error'),
               temp = '';
            if (options.length > 0) {

               errornote.innerText = '';
               errornote.classList.remove('errornote');
               
               options.forEach((elem, i) => {
                  if (i == options.length-1) {
                     temp += elem.value;
                  }
                  else {
                     temp += elem.value + ',';
                  }
               })
               
               data.append('teams', temp);
            
               fetch('',
                  {
                     method: "POST",
                     body: data
                  })
                  .then(response => {
                     if (response.redirected) return false;
            
                     if (response.ok) return response.json()
                  })
                  .then(data => {
                     console.log(data);
               })
            }
            else {
               errornote.innerText = `Вы не выбрали ни одной команды на удаление`;
               errornote.classList.add('errornote');
               return;
            } 
      
         };
      })
   }
});


function gotoEditTablePage(slug) {
   window.location = ` /tournaments/${slug}`;
}

function gotoEditTeamPage(slug) {
   window.location = `/service/admin/teams/edit/${slug}`;
}

function gotoDeleteTeamPage(slug) {
   window.location = `/service/admin/teams/delete/${slug}`;
}

function sendUserBack() {
   id = document.querySelector('input[name="get_back_url"]').value;
   window.location.replace(`/admin/tournaments/tournament/${id}/change/`);
}

function initEditTeamSelect(data) {
   let body = document.querySelector('.form-row.field-particapants'),
      submitBtn = document.querySelector('.save-btn');

   submitBtn.removeAttribute('style');

   if (!body) return;
   body.removeAttribute('style');

   let playersPlaySelect = body.querySelector('#id_particapants_to'),
      playersAvailSelect = body.querySelector('#id_particapants_from'),
      playersPlay = data['team_users_play'],
      playersAvail = [];

      console.log(playersPlay)


   if (playersPlay) {
      playersPlay.forEach(player => {
         playersPlaySelect.insertAdjacentHTML('beforeend',`<option value="${player['particapants']}" title="${player['particapants__nickname']}">${player['particapants__nickname']}</option>`)
      })

      data['team_users'].forEach((elem, index) => {
         let flag = true;
         playersPlay.forEach(player => {
            if (player['particapants'] == elem['players']) {
               flag = false;
            }
         })

         if (flag) {
            playersAvail[index] = elem;
         }
      })
   }

   playersAvail.forEach(player => {
      playersAvailSelect.insertAdjacentHTML('beforeend',`<option value="${player['players']}" title="${player['players__nickname']}">${player['players__nickname']}</option>`)
   })

   addTeamSelectFunctionallity(body, playersAvailSelect, playersPlaySelect);
}

function addTeamSelectFunctionallity(body, selectOff, selectOn) {
   let selectAllBtn = body.querySelector('.selector-chooseall'),
      deleteAllBtn = body.querySelector('.selector-clearall'),
      removeSelected = body.querySelector('.selector-remove'),
      addSelected = body.querySelector('.selector-add');

   body.addEventListener('dblclick', (e) => {
      if (e.target.tagName == 'OPTION') {
         let target = e.target,
            parent = target.parentElement;

         target.selected = false;
         if (parent.isEqualNode(selectOn)) {
            selectOff.append(target);
            removeSelected.classList.remove('active');
         }
         else {
            selectOn.append(target);
            addSelected.classList.remove('active');
         }
      }
   })

   selectAllBtn.addEventListener('click', (e) => {
      selectOn.innerHTML += selectOff.innerHTML;
      selectOff.innerHTML = '';
   })
   
   deleteAllBtn.addEventListener('click', (e) => {
      selectOff.innerHTML += selectOn.innerHTML;
      selectOn.innerHTML = '';
   })

   selectOff.addEventListener('change', (e) => {
      handleChangeE(selectOff, addSelected)
   })

   selectOn.addEventListener('change', (e) => {
      handleChangeE(selectOn, removeSelected)
   })

   function handleChangeE(select, btn) {
      btn.classList.add('active')
      let selectedOptions = select.querySelectorAll('option'),
         result = true;
      selectedOptions.forEach(elem => {
         if (elem.selected) {
            result = false;
            return;
         };
      })
      if (result) btn.classList.remove('active');
   }

   removeSelected.addEventListener('click', (e) => {
      handleClickE(selectOn, selectOff, removeSelected);
   })

   addSelected.addEventListener('click', (e) => {
      handleClickE(selectOff, selectOn, addSelected);
   })

   function handleClickE(from, to, btn) {
      if (btn.classList.contains('active')) {
         let options = from.querySelectorAll('option');

         options.forEach(option => {
            if (option.selected) {
               to.append(option);
               option.selected = false;
            }
         })
      }
   }
}

function sendTeamSelect(form, select) {
   let data = new FormData(form),
      options = select.querySelectorAll('option'),
      typo = form.querySelector('input[name="tour_typo"]').value,
      errornote = form.querySelector('.error'),
      temp = '';

   console.log(options.length != typo)
   if (options.length != typo) {
      errornote.innerText = `Вы выбрали ${options.length} игроков, когда на турнире должно быть ${typo} игроков`;
      errornote.classList.add('errornote');
      return;
   }
   else {
      errornote.innerText = '';
      errornote.classList.remove('errornote');
   } 

   options.forEach((elem, i) => {
      if (i == options.length-1) {
         temp += elem.value;
      }
      else {
         temp += elem.value + ',';
      }
   })
   
   data.append('players', temp);

   fetch('',
      {
         method: "POST",
         body: data
      })
      .then(response => {
         if (response.redirected) return false;

         if (response.ok) return response.json()
      })
      .then(data => {
         console.log(data);
   })
}

function reformPlayersField(field, slug, csrf) {
   field.querySelector('label').innerText = 'Участвующие команды:'

   let select = field.querySelector('select'),
      url = '/service/admin/getteams',
      data = new FormData();

      data.append('tournament', slug)
      data.append('csrfmiddlewaretoken', csrf)

      select.innerHTML = '';
      fetch(url,
         {
            method: "POST",
            body: data
         })
         .then(response => {
            if (response.redirected) return false;
   
            if (response.ok) return response.json()
         })
         .then(data => {
            if (!data) return;

            data['teams'].forEach(team => {
               select.insertAdjacentHTML('beforeend', `<option value="blank" style="color: #fff;">${team.team__name}</option>`)
            });

            select.nextElementSibling.remove();
            select.disabled = true;
         })
}

function sendFetch(url, data) {
   fetch(url,
      {
         method: "POST",
         credentials: "same-origin",
         body: data
      })
      .then(response => {
         if (response.redirected) return false;

         if (response.ok) data = response.json()
      })
   
   return data
}
   