from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'status', 'created_at')
    list_filter = ('status', 'project')
    search_fields = ('desc',)
