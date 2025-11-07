from django.urls import path
from .views import StartConversationView, ConversationMessagesView, SendMessageView

urlpatterns = [
    path("start/", StartConversationView.as_view(), name="start_conversation"),
    path("messages/<int:conversation_id>/", ConversationMessagesView.as_view(), name="conversation_messages"),
    path("send/", SendMessageView.as_view(), name="send_message"),
]
