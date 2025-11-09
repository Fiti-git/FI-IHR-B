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
        user = self.scope["user"]

        # --- 👇 THIS IS THE CRITICAL NEW CODE BLOCK 👇 ---

        # Add print statements for debugging
        print(f"\n[ChatConsumer] User '{user}' attempting to connect to conversation '{self.conversation_id}'")
        print(f"[ChatConsumer] User is authenticated: {user.is_authenticated}")

        # Check if the user is a participant in the conversation
        is_participant = await self.is_user_participant(user, self.conversation_id)
        
        print(f"[ChatConsumer] Is user a participant? {is_participant}")

        # If user is not logged in OR is not a participant, reject the connection
        if not user.is_authenticated or not is_participant:
            print(f"[ChatConsumer] REJECTING connection for user '{user}'.")
            await self.close()
            return

        # --- 👆 END OF NEW CODE BLOCK 👆 ---

        print(f"[ChatConsumer] ACCEPTING connection for user '{user}'.")
        # Join the room group
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
        
        # Ensure the user is authenticated before proceeding
        if not self.scope["user"].is_authenticated:
            return

        user_id = self.scope["user"].id

        if not message or not user_id:
            return

        new_message = await self.save_message(user_id, self.conversation_id, message)
        serialized = MessageSerializer(new_message).data

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": serialized}
        )

    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps(event["message"]))

    # --- 👇 THIS IS THE NEW HELPER METHOD 👇 ---
    @database_sync_to_async
    def is_user_participant(self, user, conversation_id):
        """Check if the user is a participant of the conversation."""
        if not user.is_authenticated:
            return False
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            # Check if a user with the given ID is in this conversation's participants
            return conversation.participants.filter(id=user.id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, text):
        """Save message to DB"""
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(conversation=conversation, sender=user, text=text)