from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp']
