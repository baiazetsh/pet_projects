# zz/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope["url_route"]["kwargs"]["post_id"]
        self.room_group_name = f"post_{self.post_id}"
        
        # Подписка на группу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ WS connect post={self.post_id} ch={self.channel_name}")
        
        
    async def disconnect(self, close_code):
        # Отписка
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    # Приём сообщения от клиента (если захочешь слать с фронта)
    async def receive(self, text_data):
        data = json.loads(text_data)
        comment = data["comment"]
        
        # Отправка в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "comment_message",
                "comment": data.get("comment"),
            }
        )
        
    # Хендлер для сообщений группы
    async def comment_message(self, event):
        
        await self.send(text_data=json.dumps(event))
        #comment = event["comment"]
        
        #await self.send(text_data=json.dumps({
        #    "comment": event["comment"]
        #}))
