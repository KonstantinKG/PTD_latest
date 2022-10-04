import json

from channels.generic.websocket import AsyncWebsocketConsumer
from main.models import User
from .models import Messages

from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
   groups = ['chat']

   async def connect(self):
      print(self.scope['url_route'])

      await self.channel_layer.group_add(
         'chat',
         self.channel_name
      )

      await self.accept()

   async def disconnect(self, close_code):
      await self.channel_layer.group_discard(
         'chat',
         self.channel_name
      )

   async def receive(self, text_data):
      data = json.loads(text_data)
      message = data['message']
      nickname = data['nickname']

      data = await self.save_message(nickname=nickname, message=message)

      await self.channel_layer.group_send(
         'chat',
         data
      )
   
   async def chat_message(self, event):
      message = event['message']
      nickname = event['nickname']
      pos_info = event['position']
      photo = event['photo']
      date = event['date']

      await self.send(text_data=json.dumps({
         "message": message,
         "nickname": nickname,
         "pos_info": pos_info,
         "photo": photo,
         "date": date
      }))

   @sync_to_async
   def save_message(self, nickname, message):
      data = {'type': 'chat_message'}

      user = User.objects.get(nickname=nickname)
      if user.photo: 
         photo = user.photo.url
      else:
         photo = ''

      if user.position:
         pos_info = [user.position.name, user.position.color]
      else:
         pos_info = ['','']

      ms = Messages.objects.create(message=message, user=user)

      data['nickname'] = nickname
      data['photo'] = photo
      data['position'] = pos_info
      data['message'] = message
      data['date'] = ms.date_created.strftime("%H:%M")

      return data
