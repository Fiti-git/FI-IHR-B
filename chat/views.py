from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class StartConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        other_user_id = request.data.get("user_id")

        if not other_user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if other_user == request.user:
            return Response(
                {"error": "You cannot start a chat with yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Deterministic pair key — ensures only one room per pair
        pair_key = Conversation.get_pair_key(request.user.id, other_user.id)

        # ✅ get_or_create prevents duplicate conversations
        conversation, created = Conversation.objects.get_or_create(pair_key=pair_key)

        # ✅ Only add participants if not already linked
        if created or conversation.participants.count() < 2:
            conversation.participants.add(request.user, other_user)

        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

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
        text = request.data.get("text")

        if not conversation_id or not text:
            return Response({"error": "conversation_id and text are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        if not conversation.participants.filter(id=request.user.id).exists():
            return Response({"error": "You are not a participant in this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 🟢 NEW: List all conversations for the authenticated user
class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return all conversations where the requesting user is a participant
        return Conversation.objects.filter(participants=self.request.user).order_by('-updated_at')