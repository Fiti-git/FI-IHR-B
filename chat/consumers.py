import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """When a user connects to a WebSocket room"""
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # ✅ Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """When user disconnects"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """When a message is received from the WebSocket"""
        data = json.loads(text_data)
        message = data.get("message")
        user_id = self.scope["user"].id

        if not message or not user_id:
            return

        # ✅ Save message to DB
        new_message = await self.save_message(user_id, self.conversation_id, message)

        # ✅ Serialize and send to room
        serialized = MessageSerializer(new_message).data

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": serialized
            }
        )

    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, text):
        """Save message to DB"""
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(conversation=conversation, sender=user, text=text)
