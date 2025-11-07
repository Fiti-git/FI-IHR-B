from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


# 🔹 Start or get conversation between two users
class StartConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        other_user_id = request.data.get("user_id")
        if not other_user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent starting chat with self
        if other_user == request.user:
            return Response({"error": "You cannot start a chat with yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing conversation
        conversation = (
            Conversation.objects
            .filter(participants=request.user)
            .filter(participants=other_user)
            .first()
        )

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)

        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 Pagination for messages
class MessagePagination(PageNumberPagination):
    page_size = 10
    ordering = "-timestamp"


# 🔹 View messages for a conversation
class ConversationMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Message.objects.none()

        # ✅ Ensure user belongs to this conversation
        if not conversation.participants.filter(id=self.request.user.id).exists():
            return Message.objects.none()

        return Message.objects.filter(conversation=conversation).order_by("-timestamp")


# 🔹 Send a message
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        conversation_id = request.data.get("conversation_id")
        content = request.data.get("content")

        if not conversation_id or not content:
            return Response({"error": "conversation_id and content are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Ensure sender is a participant
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response({"error": "You are not a participant in this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        # Create and serialize message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
