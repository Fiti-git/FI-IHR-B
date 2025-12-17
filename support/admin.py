from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from .models import SupportTicket
import json

# Bulk Actions
@admin.action(description="Mark selected tickets as Resolved")
def make_resolved(modeladmin, request, queryset):
    updated_count = queryset.update(status='resolved')
    modeladmin.message_user(request, f"{updated_count} ticket(s) marked as resolved.")

@admin.action(description="Mark selected tickets as Closed")
def make_closed(modeladmin, request, queryset):
    updated_count = queryset.update(status='closed')
    modeladmin.message_user(request, f"{updated_count} ticket(s) marked as closed.")

@admin.action(description="Mark selected tickets as Open")
def make_open(modeladmin, request, queryset):
    updated_count = queryset.update(status='open')
    modeladmin.message_user(request, f"{updated_count} ticket(s) marked as open.")

class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subject', 'user_link', 'ticket_type', 'category',
        'priority', 'status', 'created_at_local', 'updated_at_local', 'assigned_to_link'
    )
    list_filter = ('status', 'priority', 'category', 'ticket_type', 'created_at')
    search_fields = ('subject', 'description', 'user__username', 'reference_title')
    readonly_fields = ('created_at', 'updated_at', 'pretty_messages')
    ordering = ('-created_at',)
    actions = [make_resolved, make_closed, make_open]
    autocomplete_fields = ['user', 'assigned_to']

    fieldsets = (
        (None, {
            'fields': (
                'subject', 'user', 'ticket_type', 'reference_id', 'reference_title',
                'category', 'priority', 'status', 'assigned_to'
            )
        }),
        ('Description', {
            'fields': ('description',),
        }),
        ('Messages (Read-only)', {
            'fields': ('pretty_messages',),
            'description': 'Conversation history in JSON format',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    # Link to related user admin page
    def user_link(self, obj):
        if obj.user:
            url = f"/admin/auth/user/{obj.user.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"
    user_link.short_description = "User"
    user_link.admin_order_field = 'user__username'

    def assigned_to_link(self, obj):
        if obj.assigned_to:
            url = f"/admin/auth/user/{obj.assigned_to.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.assigned_to.username)
        return "-"
    assigned_to_link.short_description = "Assigned To"
    assigned_to_link.admin_order_field = 'assigned_to__username'

    # Format timestamps to local timezone and readable format
    def created_at_local(self, obj):
        return localtime(obj.created_at).strftime('%Y-%m-%d %H:%M:%S')
    created_at_local.short_description = 'Created At'
    created_at_local.admin_order_field = 'created_at'

    def updated_at_local(self, obj):
        return localtime(obj.updated_at).strftime('%Y-%m-%d %H:%M:%S')
    updated_at_local.short_description = 'Updated At'
    updated_at_local.admin_order_field = 'updated_at'

    # Pretty print JSON messages, safely handle errors
    def pretty_messages(self, obj):
        try:
            formatted_json = json.dumps(obj.messages, indent=2, ensure_ascii=False)
            return format_html('<pre style="white-space: pre-wrap; max-width: 700px; background: #f7f7f7; padding: 10px; border-radius: 4px;">{}</pre>', formatted_json)
        except Exception:
            return obj.messages
    pretty_messages.short_description = "Messages"

admin.site.register(SupportTicket, SupportTicketAdmin)
