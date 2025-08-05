# support/serializers.py
from rest_framework import serializers
from .models import SupportTicket

class SupportTicketSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'user', 'project', 'desc', 'docs',
            'status', 'created_at', 'updated_at', 'updated_by',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'updated_by']
