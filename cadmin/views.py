from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets,generics,permissions,status,parsers
from django.contrib.auth.models import User, Permission
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action,api_view, permission_classes, parser_classes
from support.models import SupportTicket
from .serializers import AddMessageSerializer, JobCreateSerializer
from django.contrib.auth.decorators import login_required
from chat.models import Conversation, Message
from rest_framework import generics
from .serializers import ConversationSerializer
from cms.models import ServiceCategory, Service, ServiceSubHeading, ContactMessage
from .serializers import (
    ServiceCategorySerializer, ServiceSerializer, 
    ServiceSubHeadingSerializer, ContactMessageSerializer,AdminProjectSerializer, 
    AdminProposalSerializer, 
    AdminMilestoneSerializer, 
    AdminPaymentSerializer, 
    AdminFeedbackSerializer,
    AdminProjectCreateSerializer
)
import json
from django.db.models import Sum


User = get_user_model()

class AdminUserCRUDAPIView(APIView):
    """
    Admin API to perform CRUD operations on the User model.
    """
    permission_classes = [IsAuthenticated]

    # Helper function to get user details with groups and permissions
    def get_user_data(self, user):
        group_permissions = Permission.objects.filter(group__user=user).distinct()
        all_permissions = set(list(user.user_permissions.all()) + list(group_permissions))

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "username": user.username,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "groups": [group.name for group in user.groups.all()],
            "permissions": [
                {
                    "id": permission.id,
                    "codename": permission.codename,
                    "name": permission.name,
                    "app": permission.content_type.app_label
                }
                for permission in all_permissions
            ]
        }

    # GET: List all users with permissions and groups
    def get(self, request, user_id=None): # Add user_id=None here
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return Response(self.get_user_data(user))
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # If no user_id, list all (existing logic)
        users = User.objects.all().prefetch_related('groups', 'user_permissions')
        data = [self.get_user_data(user) for user in users]
        return Response(data)

    # POST: Create a new user
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name', '')
            )

            # --- ADD THESE LINES ---
            user.is_active = data.get('is_active', True)
            user.is_staff = data.get('is_staff', False)
            # -----------------------

            if data.get('groups'):
                user.groups.set(data.get('groups'))
            if data.get('permissions'):
                user.user_permissions.set(data.get('permissions'))

            user.save()

            return Response(self.get_user_data(user), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    # PUT: Update an existing user
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name) # <--- Allow updating first_name
        
        if data.get('password'):
            user.set_password(data.get('password'))

        if data.get('groups'):
            user.groups.set(data.get('groups'))
        if data.get('permissions'):
            user.user_permissions.set(data.get('permissions'))

        user.is_active = data.get('is_active', user.is_active)
        user.is_staff = data.get('is_staff', user.is_staff)

        user.save()
        return Response(self.get_user_data(user))
    # PUT: Update an existing user
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update user fields (e.g., username, email, etc.)
        data = request.data
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        if data.get('password'):
            user.set_password(data.get('password'))  # Ensure password is hashed

        # Handle groups and permissions updates
        if data.get('groups'):
            user.groups.set(data.get('groups'))
        if data.get('permissions'):
            user.user_permissions.set(data.get('permissions'))

        user.is_active = data.get('is_active', user.is_active)
        user.is_staff = data.get('is_staff', user.is_staff)

        user.save()

        # Return updated user data with groups and permissions
        return Response(self.get_user_data(user))

    # DELETE: Delete a user
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"detail": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        

class PermissionsListAPIView(APIView):
    """
    API to list all the existing permissions in the system.
    """
    def get(self, request):
        # Fetch all permissions from the database
        permissions = Permission.objects.all()
        
        # Prepare data with permission details
        data = [
            {
                "id": permission.id,
                "codename": permission.codename,
                "name": permission.name,
                "app": permission.content_type.app_label
            }
            for permission in permissions
        ]
        
        return Response(data, status=status.HTTP_200_OK)
    

class UserPermissionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # Use prefetch_related to optimize the database query
            user = User.objects.prefetch_related('user_permissions__content_type').get(pk=pk)
            
            # Serialize user's current direct permissions
            permissions_data = [
                {
                    "id": p.id,
                    "codename": p.codename,
                    "name": p.name,
                    "app": p.content_type.app_label
                } for p in user.user_permissions.all()
            ]
            
            return Response({
                "user": {
                    "id": user.id, 
                    "email": user.email,
                    "username": user.username
                },
                "permissions": permissions_data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            
            # Ensure we are getting a list, even if 'permissions' is missing
            permission_ids = request.data.get('permissions', [])
            
            if not isinstance(permission_ids, list):
                return Response({"error": "Permissions must be a list of IDs"}, status=status.HTTP_400_BAD_REQUEST)

            # Convert all IDs to integers to prevent database type mismatch
            try:
                clean_ids = [int(pid) for pid in permission_ids]
            except (ValueError, TypeError):
                return Response({"error": "Invalid ID format in list"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the actual Permission objects to validate they exist
            # This prevents 500 errors if a fake ID is sent
            valid_permissions = Permission.objects.filter(id__in=clean_ids)
            
            # .set() replaces all existing user_permissions with the new list
            user.user_permissions.set(valid_permissions)
            
            return Response({
                "message": "Permissions updated successfully",
                "count": valid_permissions.count()
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Internal Server Error: {e}") # Check your terminal for this!
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Import your models and serializers
from support.models import SupportTicket
from .serializers import SupportTicketSerializer, MessageSerializer


class SupportTicketAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Admin to manage Support Tickets.
    - Superusers can see all tickets.
    - Staff can only see tickets assigned to them.
    - Provides an action to add messages to a ticket's chat log.
    """
    queryset = SupportTicket.objects.all().select_related('user', 'assigned_to')
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAdminUser] # Ensures only staff can access

    def get_queryset(self):
        """
        Filter tickets based on user role.
        """
        user = self.request.user

        if user.is_superuser:
            # Superusers can see all tickets
            return super().get_queryset()
        
        # Other staff members can only see tickets assigned to them
        return super().get_queryset().filter(assigned_to=user)

    @action(detail=True, methods=['post'], url_path='add-message')
    def add_message(self, request, pk=None):
        """
        Custom action to add a message to a ticket's JSON chat log.
        """
        ticket = self.get_object()
        user = request.user

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # Construct the new message object
            new_message = {
                'sender_id': user.id,
                'sender': 'support' if user.is_staff else 'user',
                'message': serializer.validated_data['text'],
                'timestamp': timezone.now().isoformat(),
            }

            # Append to the existing list of messages
            ticket.messages.append(new_message)
            ticket.save()

            # Return the full, updated ticket
            return Response(
                self.get_serializer(ticket).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'], url_path='assign-ticket')
    def assign_ticket(self, request, pk=None):
        ticket = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        new_status = request.data.get('status')

        if not assigned_to_id:
            return Response({"error": "assigned_to_id is required"}, status=400)

        ticket.assigned_to_id = assigned_to_id
        if new_status:
            ticket.status = new_status
        
        ticket.save()
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=200)
    
    @action(detail=True, methods=['post'], url_path='assign-ticket')
    def assign_ticket(self, request, pk=None):
        ticket = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        new_status = request.data.get('status')

        # Update assignment if provided
        if assigned_to_id:
            ticket.assigned_to_id = assigned_to_id
        
        # Update status if provided
        if new_status:
            # You can add a check here: if new_status in dict(SupportTicket.STATUS_CHOICES):
            ticket.status = new_status
        
        ticket.save()
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

def staff_users(request):
    # Query staff users
    staff = User.objects.filter(is_staff=True).values('id', 'first_name', 'email')

    # Return the data as JSON response (can be adjusted based on how you want to display it)
    return JsonResponse(list(staff), safe=False)


class SupportReplyView(APIView):
    permission_classes = [IsAdminUser]  # Only staff/support can reply

    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk)

        message_text = request.data.get("message")
        if not message_text or not message_text.strip():
            return Response(
                {"detail": "Message is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_message = {
            "sender": "support",
            "message": message_text.strip(),
            "sender_id": request.user.id,
            "timestamp": timezone.now().isoformat(),
        }

        # Append to messages list
        ticket.messages.append(new_message)

        # Optional: auto-update status
        if ticket.status == "open":
            ticket.status = "in_progress"

        ticket.save()

        return Response(
            {
                "detail": "Message added successfully",
                "message": new_message
            },
            status=status.HTTP_200_OK
        )
    

class UserConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = []

    def get_queryset(self):
        # This will return EVERY conversation in the DB for testing
        return Conversation.objects.all().prefetch_related('participants', 'messages')
    
#cms views

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().prefetch_related('sub_headings')
    serializer_class = ServiceSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id')
        if category_id:
            return self.queryset.filter(category_id=category_id)
        return self.queryset

class ServiceSubHeadingViewSet(viewsets.ModelViewSet):
    queryset = ServiceSubHeading.objects.all()
    serializer_class = ServiceSubHeadingSerializer
    permission_classes = [permissions.AllowAny]

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]


# --- THE MANUAL BYPASS (To fix the 405 PATCH issue) ---
# views.py (Add this function)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@parser_classes([parsers.MultiPartParser, parsers.FormParser])
def manual_service_create(request):
    """
    Explicit function-based view to handle creation.
    """
    # Use the serializer to validate and save
    serializer = ServiceSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

@api_view(['PATCH', 'PUT'])
@permission_classes([permissions.AllowAny])
@parser_classes([parsers.MultiPartParser, parsers.FormParser])
def manual_service_update(request, pk):
    """
    Explicit function-based view to handle updates when 
    the router/viewset is blocked by 405 errors.
    """
    try:
        service = Service.objects.get(pk=pk)
    except Service.DoesNotExist:
        return Response({"detail": "Service not found"}, status=404)

    # Note: partial=True allows PATCH requests to work
    serializer = ServiceSerializer(service, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)
    def get_queryset(self):
        # Filtering by category if needed, otherwise return all
        category_id = self.request.query_params.get('category_id')
        if category_id:
            return self.queryset.filter(category_id=category_id)
        return self.queryset
class ServiceSubHeadingViewSet(viewsets.ModelViewSet):
    queryset = ServiceSubHeading.objects.all()
    serializer_class = ServiceSubHeadingSerializer

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer


#choice manger

from rest_framework import viewsets, filters
from choices_manager.models import ChoiceGroup, ChoiceItem
from .serializers import ChoiceGroupSerializer, ChoiceItemSerializer

class ChoiceGroupViewSet(viewsets.ModelViewSet):
    queryset = ChoiceGroup.objects.all()
    serializer_class = ChoiceGroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']

class ChoiceItemViewSet(viewsets.ModelViewSet):
    queryset = ChoiceItem.objects.all()
    serializer_class = ChoiceItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['label', 'value']

    def get_queryset(self):
        # Allow filtering by group ID (important for your frontend drill-down)
        queryset = ChoiceItem.objects.all()
        group_id = self.request.query_params.get('group_id')
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        return queryset
    

# Profile views can be added here as needed

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from profiles.models import FreelancerProfile, JobProviderProfile
from .serializers import FreelancerProfileSerializer, JobProviderProfileSerializer
from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework import status, permissions

class AdminPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get('search', '')
        role_filter = request.query_params.get('role', '')

        all_results = []

        # 1. Fetch Freelancers
        if not role_filter or role_filter == 'freelancer':
            freelancers = FreelancerProfile.objects.filter(
                Q(full_name__icontains=search) | Q(user__email__icontains=search)
            ).order_by('-created_at')
            fl_data = FreelancerProfileSerializer(freelancers, many=True).data
            all_results.extend(fl_data)

        # 2. Fetch Employers
        if not role_filter or role_filter == 'employer':
            employers = JobProviderProfile.objects.filter(
                Q(company_name__icontains=search) | Q(user__email__icontains=search)
            ).order_by('-created_at')
            emp_data = JobProviderProfileSerializer(employers, many=True).data
            all_results.extend(emp_data)

        # 3. Sort combined list by date
        all_results.sort(key=lambda x: x['created_at'], reverse=True)

        # 4. Paginate the manual list
        paginator = AdminPagination()
        page = paginator.paginate_queryset(all_results, request)
        
        return paginator.get_paginated_response(page)
    
class AdminProfileDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, role, id):
        profile = self.get_object(role, id)
        serializer = self.get_serializer(role, profile)
        return Response(serializer.data)

    def patch(self, request, role, id):
        profile = self.get_object(role, id)
        serializer = self.get_serializer(role, profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, role, id):
        if role == 'freelancer':
            return get_object_or_404(FreelancerProfile, id=id)
        return get_object_or_404(JobProviderProfile, id=id)

    def get_serializer(self, role, *args, **kwargs):
        if role == 'freelancer':
            return FreelancerProfileSerializer(*args, **kwargs)
        return JobProviderProfileSerializer(*args, **kwargs)
    
class AdminCreateUserView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Fetch all available groups for the frontend dropdown."""
        groups = Group.objects.all().values('id', 'name')
        return Response(groups)

    @transaction.atomic
    def post(self, request):
        data = request.data
        files = request.FILES
        
        # 1. Extraction & Validation
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        group_name = data.get('group') # Expecting 'Freelancer' or 'Employer'
        
        # Basic field validation
        if not all([email, username, password, group_name]):
            return Response({"error": "Missing required authentication fields."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Create the Django Auth User
            # Note: FormData sends booleans as strings "true"/"false"
            is_active_val = data.get('is_active') == 'true'
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=data.get('first_name', ''),
                is_active=is_active_val
            )

            # 3. Assign Group
            group = Group.objects.get(name=group_name)
            user.groups.add(group)

            # 4. Create Profile based on Group
            if group_name.lower() == 'freelancer' or group_name.lower() == 'candidate':
                FreelancerProfile.objects.create(
                    user=user,
                    full_name=data.get('full_name') or data.get('first_name'),
                    phone_number=data.get('phone_number'),
                    professional_title=data.get('professional_title'),
                    hourly_rate=data.get('hourly_rate'),
                    gender=data.get('gender'),
                    experience_level=data.get('experience_level'),
                    specialization=data.get('specialization'),
                    skills=data.get('skills'),
                    country=data.get('country'),
                    city=data.get('city'),
                    language=data.get('language'),
                    language_proficiency=data.get('language_proficiency'),
                    linkedin_or_github=data.get('linkedin_or_github'),
                    bio=data.get('bio'),
                    profile_image=files.get('profile_image'),
                    resume=files.get('resume'),
                    is_active=is_active_val,
                    role_fillter='freelancer'
                )
                role_path = 'freelancer'
            
            elif group_name.lower() == 'employer':
                JobProviderProfile.objects.create(
                    user=user,
                    company_name=data.get('company_name') or data.get('first_name'),
                    email_address=email,
                    phone_number=data.get('phone_number'),
                    company_overview=data.get('company_overview'),
                    job_type=data.get('job_type'),
                    industry=data.get('industry'),
                    country=data.get('country'),
                    profile_image=files.get('profile_image'),
                    is_active=is_active_val
                )
                role_path = 'employer'
            
            else:
                # Rollback if group is invalid
                transaction.set_rollback(True)
                return Response({"error": f"Invalid group selection: {group_name}"}, status=400)

            return Response({
                "message": "User and Profile created successfully",
                "user_id": user.id,
                "role": role_path
            }, status=status.HTTP_201_CREATED)

        except Group.DoesNotExist:
            return Response({"error": "Selected group does not exist in the database."}, status=400)
        except Exception as e:
            # If any error occurs, transaction.atomic will automatically rollback the user creation
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# Project views can be added here as needed
from rest_framework import generics, permissions
from project.models import Project, Proposal, Milestone, MilestonePayment,Feedback
from .serializers import (
    AdminProjectSerializer, AdminProposalSerializer, 
    AdminMilestoneSerializer, AdminPaymentSerializer, AdminFeedbackSerializer
)
class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_projects = Project.objects.count()
        pending_bids = Proposal.objects.filter(status='submitted').count()
        completed_projects = Project.objects.filter(status='completed').count()

        return Response({
            "total_projects": total_projects,
            "pending_bids": pending_bids,
            "completed_projects": completed_projects
        })

# --- PROJECT MANAGEMENT ---

class AdminProjectListView(generics.ListCreateAPIView):
    """
    List all projects with basic info for the table view.
    """
    queryset = Project.objects.select_related('user__job_provider_profile').all().order_by('-created_at')
    serializer_class = AdminProjectSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProjectSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Project.objects.select_related(
            'user__job_provider_profile'
        ).prefetch_related(
            # Path: Proposals -> Freelancer User -> FreelancerProfile
            'proposals__freelancer__freelancer_profile', 
            'milestones'
        ).all()

# --- PROPOSAL MANAGEMENT ---

class AdminProposalListView(generics.ListCreateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = AdminProposalSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Manage specific proposals (Approve/Reject bids).
    """
    queryset = Proposal.objects.select_related('user__freelancer_profile').all()
    serializer_class = AdminProposalSerializer
    permission_classes = [permissions.IsAdminUser]

# --- MILESTONE MANAGEMENT ---

class AdminMilestoneListView(generics.ListCreateAPIView):
    queryset = Milestone.objects.all()
    serializer_class = AdminMilestoneSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminMilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Milestone.objects.all()
    serializer_class = AdminMilestoneSerializer
    permission_classes = [permissions.IsAdminUser]

# --- PAYMENT & FEEDBACK ---

class AdminPaymentListView(generics.ListAPIView):
    queryset = MilestonePayment.objects.select_related('milestone', 'milestone__project').all()
    serializer_class = AdminPaymentSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminFeedbackListView(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = AdminFeedbackSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminAllFreelancersView(generics.ListAPIView):
    queryset = FreelancerProfile.objects.all()
    serializer_class = FreelancerProfileSerializer
    permission_classes = [permissions.IsAdminUser]

# --- Create Project ---
# View to create the project
class AdminProjectCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = AdminProjectCreateSerializer
    permission_classes = [permissions.IsAdminUser]

# View to fetch all employers for the selection sidebar
class AdminEmployerListView(generics.ListAPIView):
    queryset = JobProviderProfile.objects.all()
    serializer_class = JobProviderProfileSerializer
    permission_classes = [permissions.IsAdminUser]


# --- Job ---

from rest_framework import viewsets, permissions,status
from jobs.models import JobPosting, JobApplication
from .serializers import AdminJobListingSerializer,JobDetailSerializer
from rest_framework.response import Response

class AdminJobPostingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admin to view all job postings 
    with nested provider details.
    """
    queryset = JobPosting.objects.select_related('job_provider', 'assigned_to').all()
    serializer_class = AdminJobListingSerializer
    permission_classes = [permissions.IsAdminUser] # Uncomment to restrict access



class JobPostingCRUDViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobDetailSerializer
        return AdminJobListingSerializer

    @action(detail=True, methods=['post'], url_path='assign-candidate')
    def assign_candidate(self, request, pk=None):
        """
        Manually assign a freelancer to this job using their existing profile data.
        """
        job = self.get_object()
        freelancer_user_id = request.data.get('freelancer_id')
        note = request.data.get('reference_note', '')

        if not freelancer_user_id:
            return Response({"detail": "freelancer_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Get the freelancer profile to access their resume
        try:
            freelancer_profile = FreelancerProfile.objects.get(user_id=freelancer_user_id)
        except FreelancerProfile.DoesNotExist:
            return Response({"detail": "Freelancer profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # 2. Prevent duplicate applications
        if JobApplication.objects.filter(job=job, freelancer_id=freelancer_user_id).exists():
            return Response({"detail": "This candidate is already assigned to this job."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create the JobApplication using the freelancer's existing resume
        # We take freelancer_profile.resume and pass it to JobApplication.resume
        new_application = JobApplication.objects.create(
            job=job,
            freelancer_id=freelancer_user_id,
            status='Pending',
            resume=freelancer_profile.resume, # This copies the file reference
            reference_added_by_admin=note
        )

        return Response({
            "message": "Candidate assigned successfully with resume",
            "application_id": new_application.id
        }, status=status.HTTP_201_CREATED)
    
# --- Create Job ---
    
class AdminJobCreateViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobCreateSerializer
    permission_classes = [permissions.IsAdminUser] # Ensure only admins can post

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)