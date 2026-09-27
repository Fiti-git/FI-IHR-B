from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import SupportTicket
from django.contrib.auth.models import User


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
  #  change_form_template = "admin/support/supportticket/change_form.html"

    list_display = (
        "id",
        "subject",
        "user",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    )

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        ("Ticket Reference", {"fields": ("ticket_type", "reference_id", "reference_title")}),
        ("Ticket Content", {"fields": ("category", "subject", "description")}),
        ("Status & Assignment", {"fields": ("status", "priority", "assigned_to")}),
        ("Chat Messages", {"fields": ("messages",)}),
        ("System Info", {"fields": ("created_at", "updated_at")}),
    )

    # ----------------------------
    # Restrict tickets to assigned user
    # ----------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(assigned_to=request.user)

    # ----------------------------
    # Restrict editing to assigned user
    # ----------------------------
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # List view
        return obj.assigned_to == request.user

    # ----------------------------
    # Disable deletion completely
    # ----------------------------
    def has_delete_permission(self, request, obj=None):
        return False

    # ----------------------------
    # Lock form if ticket is closed
    # ----------------------------
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == "closed":
            return [f.name for f in obj._meta.fields]
        return self.readonly_fields

    # ----------------------------
    # Custom admin URLs for AJAX
    # ----------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:ticket_id>/reply/",
                self.admin_site.admin_view(self.ajax_reply),
                name="supportticket_reply",
            ),
            path(
                "<int:ticket_id>/set-status/<str:status>/",
                self.admin_site.admin_view(self.ajax_set_status),
                name="supportticket_set_status",
            ),
        ]
        return custom_urls + urls

    # ----------------------------
    # AJAX: add a reply
    # ----------------------------
    @method_decorator(csrf_exempt)
    def ajax_reply(self, request, ticket_id):
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request"}, status=400)

        ticket = SupportTicket.objects.get(pk=ticket_id)
        # Ensure only assigned user or superuser can reply
        if not request.user.is_superuser and ticket.assigned_to != request.user:
            return JsonResponse({"error": "Not allowed"}, status=403)

        message = request.POST.get("message", "").strip()
        if not message:
            return JsonResponse({"error": "Empty message"}, status=400)

        ticket.messages.append({
            "sender": "support",
            "sender_id": request.user.id,
            "message": message,
            "timestamp": timezone.now().isoformat(),
        })

        ticket.save(update_fields=["messages", "updated_at"])
        return JsonResponse({"success": True})

    # ----------------------------
    # AJAX: set status (resolve/close)
    # ----------------------------
    @method_decorator(csrf_exempt)
    def ajax_set_status(self, request, ticket_id, status):
        if status not in ["resolved", "closed"]:
            return JsonResponse({"error": "Invalid status"}, status=400)

        ticket = SupportTicket.objects.get(pk=ticket_id)
        # Ensure only assigned user or superuser can change status
        if not request.user.is_superuser and ticket.assigned_to != request.user:
            return JsonResponse({"error": "Not allowed"}, status=403)

        old_status = ticket.status
        ticket.status = status

        ticket.messages.append({
            "sender": "system",
            "message": f"Ticket status changed from {old_status} to {status}",
            "timestamp": timezone.now().isoformat(),
        })

        ticket.save(update_fields=["status", "messages", "updated_at"])
        return JsonResponse({"success": True, "status": status})
