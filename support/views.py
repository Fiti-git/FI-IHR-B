# support/views.py
from rest_framework import viewsets, permissions
from .models import SupportTicket
from .serializers import SupportTicketSerializer

class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all().order_by('-created_at')
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['project', 'status']

    def perform_create(self, serializer):
        # creator is set via `user`
        serializer.save(user=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        # stamp who made this update
        serializer.save(updated_by=self.request.user)
