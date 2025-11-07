from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")
    pair_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        names = [user.username for user in self.participants.all()]
        return f"Conversation between: {', '.join(names)}"

    @staticmethod
    def get_pair_key(user1_id, user2_id):
        """Generate a deterministic pair key like '1_6' (smaller ID first)."""
        return f"{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]
