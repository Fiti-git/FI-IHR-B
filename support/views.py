from django.contrib.auth.models import User,Group
from django.http import JsonResponse
from django.views import View

from project.models import Project
from jobs.models import JobPosting
from profiles.models import JobProviderProfile
from django.utils.timezone import now
import json
from .models import SupportTicket
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class UserEngagementAPIView(View):
    """
    TESTING ONLY API
    Returns engaged projects and jobs based on user role
    """

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        groups = list(user.groups.values_list('name', flat=True))

        response_data = {
            "user_id": user.id,
            "username": user.username,
            "role": groups,
            "projects": [],
            "jobs": [],
        }

        # -----------------------
        # JOB PROVIDER
        # -----------------------
        if "Job Provider" in groups:
            projects = Project.objects.filter(user=user)

            try:
                job_provider = JobProviderProfile.objects.get(user=user)
                jobs = JobPosting.objects.filter(job_provider=job_provider)
            except JobProviderProfile.DoesNotExist:
                jobs = JobPosting.objects.none()

        # -----------------------
        # FREELANCER
        # -----------------------
        elif "Freelancer" in groups:
            projects = Project.objects.filter(
                proposals__freelancer_id=user.id
            ).distinct()

            jobs = JobPosting.objects.filter(
                jobapplication__freelancer_id=user.id
            ).distinct()

        else:
            projects = Project.objects.none()
            jobs = JobPosting.objects.none()

        # ✅ MINIMAL PROJECT OUTPUT
        for p in projects:
            response_data["projects"].append({
                "id": p.id,
                "title": p.title,
                "status": p.status,
            })

        # ✅ MINIMAL JOB OUTPUT
        for j in jobs:
            response_data["jobs"].append({
                "id": j.id,
                "job_title": j.job_title,
                "job_status": j.job_status,
            })

        return JsonResponse(response_data, safe=False)
@method_decorator(csrf_exempt, name='dispatch')  
class CreateSupportTicketAPIView(View):
    """
    TESTING ONLY
    Create a support ticket for Project or Job
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # -------------------------
        # REQUIRED FIELDS
        # -------------------------
        required_fields = [
            "user_id",
            "ticket_type",
            "reference_id",
            "reference_title",
            "category",
            "subject",
            "description",
        ]

        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"{field} is required"},
                    status=400
                )

        # -------------------------
        # USER
        # -------------------------
        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # -------------------------
        # INITIAL MESSAGE (JSON)
        # -------------------------
        initial_message = [{
            "sender": "user",
            "sender_id": user.id,
            "message": data["description"],
            "timestamp": now().isoformat()
        }]

        # -------------------------
        # CREATE TICKET
        # -------------------------
        ticket = SupportTicket.objects.create(
            user=user,
            ticket_type=data["ticket_type"],
            reference_id=data["reference_id"],
            reference_title=data["reference_title"],
            category=data["category"],
            subject=data["subject"],
            description=data["description"],
            priority=data.get("priority", "medium"),
            messages=initial_message,
        )

        return JsonResponse({
            "message": "Ticket created successfully",
            "ticket_id": ticket.id,
            "status": ticket.status,
            "created_at": ticket.created_at
        }, status=201)
@method_decorator(csrf_exempt, name='dispatch') 
class AddTicketMessageAPIView(View):
    """
    TESTING ONLY
    Append a message to an existing support ticket
    """

    def post(self, request, ticket_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # -------------------------
        # REQUIRED FIELDS
        # -------------------------
        required_fields = ["sender", "sender_id", "message"]

        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"{field} is required"},
                    status=400
                )

        # -------------------------
        # GET TICKET
        # -------------------------
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
        except SupportTicket.DoesNotExist:
            return JsonResponse({"error": "Ticket not found"}, status=404)

        # -------------------------
        # VALIDATE USER
        # -------------------------
        try:
            sender_user = User.objects.get(id=data["sender_id"])
        except User.DoesNotExist:
            return JsonResponse({"error": "Sender user not found"}, status=404)

        # -------------------------
        # APPEND MESSAGE
        # -------------------------
        new_message = {
            "sender": data["sender"],  # "user" or "support"
            "sender_id": sender_user.id,
            "message": data["message"],
            "timestamp": now().isoformat()
        }

        messages = ticket.messages or []
        messages.append(new_message)

        ticket.messages = messages

        # -------------------------
        # AUTO STATUS UPDATE
        # -------------------------
        if data["sender"] == "support" and ticket.status == "open":
            ticket.status = "in_progress"

        ticket.save()

        return JsonResponse({
            "message": "Message added successfully",
            "ticket_id": ticket.id,
            "current_status": ticket.status,
            "last_message": new_message
        }, status=200)
    
class TicketListAPIView(View):
    """
    TESTING ONLY
    List support tickets based on user role
    """

    def get(self, request, user_id):
        # -------------------------
        # GET USER
        # -------------------------
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # -------------------------
        # GET USER ROLES
        # -------------------------
        roles = list(
            Group.objects.filter(user=user).values_list("name", flat=True)
        )

        # -------------------------
        # FETCH TICKETS BASED ON ROLE
        # -------------------------
        if user.is_staff or "Support" in roles:
            tickets = SupportTicket.objects.all()
        else:
            tickets = SupportTicket.objects.filter(user=user)

        # -------------------------
        # SERIALIZE RESPONSE
        # -------------------------
        ticket_list = []
        for ticket in tickets:
            ticket_list.append({
                "id": ticket.id,
                "subject": ticket.subject,
                "category": ticket.category,
                "status": ticket.status,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at,
                "ticket_type": ticket.ticket_type,
                "reference_id": ticket.reference_id,
                "reference_title": ticket.reference_title,
            })

        return JsonResponse({
            "user_id": user.id,
            "username": user.username,
            "roles": roles,
            "total_tickets": tickets.count(),
            "tickets": ticket_list
        }, status=200)
    
class TicketDetailAPIView(View):
    """
    TESTING ONLY
    Get full details of a single support ticket
    """

    def get(self, request, ticket_id):
        # -------------------------
        # GET TICKET
        # -------------------------
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
        except SupportTicket.DoesNotExist:
            return JsonResponse({"error": "Ticket not found"}, status=404)

        user = ticket.user

        # -------------------------
        # USER ROLES
        # -------------------------
        roles = list(
            Group.objects.filter(user=user).values_list("name", flat=True)
        )

        # -------------------------
        # SERIALIZE MESSAGES
        # -------------------------
        messages = ticket.messages or []

        # -------------------------
        # RESPONSE
        # -------------------------
        return JsonResponse({
            "ticket": {
                "id": ticket.id,
                "subject": ticket.subject,
                "description": ticket.description,
                "category": ticket.category,
                "status": ticket.status,
                "priority": ticket.priority,
                "ticket_type": ticket.ticket_type,
                "reference_id": ticket.reference_id,
                "reference_title": ticket.reference_title,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at,
            },
            "user": {
                "id": user.id,
                "username": user.username,
                "roles": roles
            },
            "messages": messages
        }, status=200)
    
@method_decorator(csrf_exempt, name='dispatch')   
class UpdateTicketStatusAPIView(View):
    """
    TESTING ONLY
    Update ticket status (open, in_progress, resolved, closed)
    """

    def patch(self, request, ticket_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # -------------------------
        # REQUIRED FIELD
        # -------------------------
        if "status" not in data:
            return JsonResponse(
                {"error": "status is required"},
                status=400
            )

        allowed_statuses = ["open", "in_progress", "resolved", "closed"]

        if data["status"] not in allowed_statuses:
            return JsonResponse(
                {"error": f"Status must be one of {allowed_statuses}"},
                status=400
            )

        # -------------------------
        # GET TICKET
        # -------------------------
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
        except SupportTicket.DoesNotExist:
            return JsonResponse({"error": "Ticket not found"}, status=404)

        old_status = ticket.status
        new_status = data["status"]

        ticket.status = new_status

        # -------------------------
        # OPTIONAL SYSTEM MESSAGE
        # -------------------------
        if "updated_by" in data and "updated_by_id" in data:
            try:
                updater = User.objects.get(id=data["updated_by_id"])
            except User.DoesNotExist:
                return JsonResponse({"error": "Updater user not found"}, status=404)

            status_message = {
                "sender": data["updated_by"],  # "support" or "system"
                "sender_id": updater.id,
                "message": f"Ticket status changed from {old_status} to {new_status}",
                "timestamp": now().isoformat()
            }

            messages = ticket.messages or []
            messages.append(status_message)
            ticket.messages = messages

        ticket.save()

        return JsonResponse({
            "message": "Ticket status updated successfully",
            "ticket_id": ticket.id,
            "old_status": old_status,
            "new_status": new_status
        }, status=200)