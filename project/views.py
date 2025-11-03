from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone

from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag
from .serializers import (
    ProjectSerializer, ProposalSerializer, MilestoneSerializer,
    MilestonePaymentSerializer, FeedbackSerializer, ProjectTagSerializer
)


def get_user_profile_type(user):
    """
    Helper function to determine user profile type
    Returns: 'freelancer', 'job-provider', or None
    """
    # Import models here to avoid circular imports
    from profiles.models import FreelancerProfile, JobProviderProfile
    
    # Check if user has freelancer profile
    try:
        FreelancerProfile.objects.get(user=user)
        return 'freelancer'
    except FreelancerProfile.DoesNotExist:
        pass
    
    # Check if user has job provider profile
    try:
        JobProviderProfile.objects.get(user=user)
        return 'job-provider'
    except JobProviderProfile.DoesNotExist:
        pass
    
    return None


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects.
    Provides CRUD operations for projects.
    
    List and Retrieve: Anyone can access (AllowAny)
    Create, Update, Delete: Authentication required (IsAuthenticated)
    
    IMPORTANT: Only Job Providers can create projects, NOT Freelancers
    """
    queryset = Project.objects.all().select_related('user').order_by('-created_at')
    serializer_class = ProjectSerializer
    
    def get_permissions(self):
        """
        Allow anyone to list/retrieve projects
        Require authentication for create/update/delete
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Create project with authenticated user
        ONLY JOB PROVIDERS CAN CREATE PROJECTS - FREELANCERS ARE BLOCKED
        """
        user = self.request.user
        profile_type = get_user_profile_type(user)
        
        print(f"DEBUG: User: {user.username}, Profile Type: {profile_type}")
        
        # Block freelancers
        if profile_type == 'freelancer':
            raise PermissionDenied(
                "Freelancers cannot create projects. Only job providers can create projects. "
                "Freelancers can only submit proposals for existing projects."
            )
        
        # Require job provider profile
        if profile_type != 'job-provider':
            raise PermissionDenied(
                "You must have a job provider profile to create projects. "
                "Please complete your profile setup."
            )
        
        # All checks passed - create the project
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """
        Update project - ensure user owns the project
        """
        project = self.get_object()
        if project.user != self.request.user:
            raise PermissionDenied("You don't have permission to edit this project")
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete project - ensure user owns the project
        """
        if instance.user != self.request.user:
            raise PermissionDenied("You don't have permission to delete this project")
        instance.delete()
    
    def get_queryset(self):
        """
        Filter projects based on query parameters
        """
        queryset = Project.objects.all().select_related('user').order_by('-created_at')
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by user (client's projects)
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by visibility
        visibility = self.request.query_params.get('visibility', None)
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        
        # Filter by project type
        project_type = self.request.query_params.get('project_type', None)
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Search by title or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_tag(self, request, pk=None):
        """Add a tag to a project"""
        project = self.get_object()
        
        # Check if user owns the project
        if project.user != request.user:
            return Response(
                {'error': 'You do not have permission to add tags to this project'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        tag_name = request.data.get('tag')
        
        if not tag_name:
            return Response(
                {'error': 'Tag name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tag, created = ProjectTag.objects.get_or_create(project=project, tag=tag_name)
        serializer = ProjectTagSerializer(tag)
        
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def tags(self, request, pk=None):
        """Get all tags for a project"""
        project = self.get_object()
        tags = ProjectTag.objects.filter(project=project)
        serializer = ProjectTagSerializer(tags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_projects(self, request):
        """Get all projects created by the authenticated user"""
        projects = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class ProposalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing proposals.
    Freelancers can submit proposals for projects.
    
    IMPORTANT: Only Freelancers can submit proposals, NOT Job Providers
    """
    queryset = Proposal.objects.all().select_related('freelancer', 'project').order_by('-submitted_at')
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow anyone to list proposals
        Require authentication for other actions
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Create proposal with authenticated user as freelancer
        ONLY FREELANCERS CAN SUBMIT PROPOSALS - JOB PROVIDERS ARE BLOCKED
        """
        user = self.request.user
        profile_type = get_user_profile_type(user)
        
        print(f"DEBUG: User: {user.username}, Profile Type: {profile_type}")
        
        # Block job providers
        if profile_type == 'job-provider':
            raise PermissionDenied(
                "Job providers cannot submit proposals. Only freelancers can submit proposals. "
                "Job providers can only create projects and review proposals."
            )
        
        # Require freelancer profile
        if profile_type != 'freelancer':
            raise PermissionDenied(
                "You must have a freelancer profile to submit proposals. "
                "Please complete your profile setup."
            )
        
        # Check if freelancer already submitted a proposal for this project
        project = serializer.validated_data.get('project')
        existing_proposal = Proposal.objects.filter(
            project=project,
            freelancer=user
        ).first()
        
        if existing_proposal:
            raise PermissionDenied(
                "You have already submitted a proposal for this project. "
                "You can edit your existing proposal instead."
            )
        
        serializer.save(freelancer=self.request.user)
    
    def perform_update(self, serializer):
        """
        Update proposal - ensure user owns the proposal
        """
        proposal = self.get_object()
        if proposal.freelancer != self.request.user:
            raise PermissionDenied("You don't have permission to edit this proposal")
        
        # Don't allow editing accepted or rejected proposals
        if proposal.status in ['accepted', 'rejected']:
            raise PermissionDenied(f"Cannot edit {proposal.status} proposals")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete proposal - ensure user owns the proposal and it's pending
        """
        if instance.freelancer != self.request.user:
            raise PermissionDenied("You don't have permission to delete this proposal")
        
        if instance.status != 'pending':
            raise PermissionDenied("Can only delete pending proposals")
        
        instance.delete()
    
    def get_queryset(self):
        """Filter proposals based on query parameters"""
        queryset = Proposal.objects.all().select_related('freelancer', 'project').order_by('-submitted_at')
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by freelancer
        freelancer_id = self.request.query_params.get('freelancer_id', None)
        if freelancer_id:
            queryset = queryset.filter(freelancer_id=freelancer_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """Accept a proposal - only project owner can accept"""
        proposal = self.get_object()
        
        # Check if user owns the project
        if proposal.project.user != request.user:
            return Response(
                {'error': 'Only project owner can accept proposals'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        proposal.status = 'accepted'
        proposal.save()
        serializer = self.get_serializer(proposal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject a proposal - only project owner can reject"""
        proposal = self.get_object()
        
        # Check if user owns the project
        if proposal.project.user != request.user:
            return Response(
                {'error': 'Only project owner can reject proposals'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        proposal.status = 'rejected'
        proposal.save()
        serializer = self.get_serializer(proposal)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_proposals(self, request):
        """Get all proposals submitted by the authenticated user"""
        proposals = self.get_queryset().filter(freelancer=request.user)
        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)


class MilestoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing milestones.
    Only freelancers with accepted proposals can create milestones.
    """
    queryset = Milestone.objects.all().select_related('freelancer', 'project').order_by('-created_at')
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow anyone to list/retrieve milestones
        Require authentication for other actions
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Create milestone - only freelancers with accepted proposals can create
        Auto-assign the authenticated user as the freelancer
        """
        project = serializer.validated_data.get('project')
        
        # Check if user is the project owner
        if project.user == self.request.user:
            raise PermissionDenied("Project owners cannot create milestones. Only assigned freelancers can.")
        
        # Check if the user has an accepted proposal for this project
        accepted_proposal = Proposal.objects.filter(
            project=project,
            freelancer=self.request.user,
            status='accepted'
        ).first()
        
        if not accepted_proposal:
            raise PermissionDenied("You do not have an accepted proposal for this project")
        
        # Auto-assign the authenticated user as the freelancer
        serializer.save(freelancer=self.request.user)
    
    def perform_update(self, serializer):
        """
        Update milestone - ensure user is the assigned freelancer or project owner
        """
        milestone = self.get_object()
        if milestone.freelancer != self.request.user and milestone.project.user != self.request.user:
            raise PermissionDenied("You don't have permission to edit this milestone")
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete milestone - ensure user is the assigned freelancer or project owner
        """
        if instance.freelancer != self.request.user and instance.project.user != self.request.user:
            raise PermissionDenied("You don't have permission to delete this milestone")
        
        # Don't allow deletion of approved milestones
        if instance.status == 'approved':
            raise PermissionDenied("Cannot delete approved milestones")
        
        instance.delete()
    
    def get_queryset(self):
        """Filter milestones based on query parameters"""
        queryset = Milestone.objects.all().select_related('freelancer', 'project').order_by('-created_at')
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by freelancer
        freelancer_id = self.request.query_params.get('freelancer_id', None)
        if freelancer_id:
            queryset = queryset.filter(freelancer_id=freelancer_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def verify_freelancer_access(self, request):
        """
        Verify if the authenticated user is a freelancer with an accepted proposal
        for the specified project.
        """
        project_id = request.query_params.get('project_id', None)
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is the project owner (client)
        if project.user == request.user:
            return Response(
                {
                    'has_access': False,
                    'error': 'Project owners cannot create milestones. Only assigned freelancers can.',
                    'is_project_owner': True
                }, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if the user has an accepted proposal for this project
        accepted_proposal = Proposal.objects.filter(
            project=project,
            freelancer=request.user,
            status='accepted'
        ).first()
        
        if not accepted_proposal:
            return Response(
                {
                    'has_access': False,
                    'error': 'You do not have an accepted proposal for this project',
                    'is_project_owner': False
                }, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({
            'has_access': True,
            'project_id': project.id,
            'project_name': project.title,
            'proposal_id': accepted_proposal.id,
            'freelancer_id': request.user.id,
            'freelancer_username': request.user.username,
            'is_project_owner': False
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_milestones(self, request):
        """Get all milestones for the authenticated freelancer"""
        milestones = self.get_queryset().filter(freelancer=request.user)
        
        # Filter by project if specified
        project_id = request.query_params.get('project_id', None)
        if project_id:
            milestones = milestones.filter(project_id=project_id)
        
        page = self.paginate_queryset(milestones)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(milestones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Mark milestone as completed - only freelancer can mark as complete"""
        milestone = self.get_object()
        
        # Check if user is the freelancer
        if milestone.freelancer != request.user:
            return Response(
                {'error': 'Only assigned freelancer can mark milestone as completed'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if milestone is in progress
        if milestone.status != 'in_progress':
            return Response(
                {'error': 'Only milestones in progress can be marked as completed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        milestone.status = 'completed'
        milestone.save()
        serializer = self.get_serializer(milestone)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Approve a milestone - only project owner can approve
        Two scenarios:
        1. Approve milestone setup (pending -> approved)
        2. Approve completed work (completed -> approved/paid)
        """
        milestone = self.get_object()
        
        # Check if user owns the project
        if milestone.project.user != request.user:
            return Response(
                {'error': 'Only project owner can approve milestones'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Scenario 1: Approve milestone setup (pending -> approved)
        if milestone.status == 'pending':
            milestone.status = 'approved'
            milestone.save()
            serializer = self.get_serializer(milestone)
            return Response({
                'message': 'Milestone setup approved successfully. Freelancer can now start working.',
                'milestone': serializer.data
            })
        
        # Scenario 2: Approve completed work (completed -> approved)
        elif milestone.status == 'completed':
            milestone.status = 'approved'
            milestone.save()
            serializer = self.get_serializer(milestone)
            return Response({
                'message': 'Milestone work approved successfully. You can now create payment.',
                'milestone': serializer.data
            })
        
        else:
            return Response(
                {
                    'error': f'Milestone with status "{milestone.status}" cannot be approved. Only pending or completed milestones can be approved.'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )


class MilestonePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing milestone payments.
    """
    queryset = MilestonePayment.objects.all().select_related('freelancer', 'project', 'milestone').order_by('-created_at')
    serializer_class = MilestonePaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow anyone to list/retrieve payments
        Require authentication for other actions
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Create payment - only project owner can create payments
        """
        project = serializer.validated_data.get('project')
        
        # Check if user owns the project
        if project.user != self.request.user:
            raise PermissionDenied("Only project owner can create payments")
        
        serializer.save()
    
    def get_queryset(self):
        """Filter payments based on query parameters"""
        queryset = MilestonePayment.objects.all().select_related('freelancer', 'project', 'milestone').order_by('-created_at')
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by freelancer
        freelancer_id = self.request.query_params.get('freelancer_id', None)
        if freelancer_id:
            queryset = queryset.filter(freelancer_id=freelancer_id)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status', None)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by milestone
        milestone_id = self.request.query_params.get('milestone_id', None)
        if milestone_id:
            queryset = queryset.filter(milestone_id=milestone_id)
        
        return queryset
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def release_payment(self, request, pk=None):
        """Release payment to freelancer - only project owner can release"""
        payment = self.get_object()
        
        # Check if user owns the project
        if payment.project.user != request.user:
            return Response(
                {'error': 'Only project owner can release payments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if payment.payment_status == 'released':
            return Response(
                {'error': 'Payment has already been released'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.payment_status = 'released'
        payment.released_at = timezone.now()
        payment.save()
        
        # Update milestone status to 'paid'
        if payment.milestone:
            payment.milestone.status = 'paid'
            payment.milestone.save()
        
        serializer = self.get_serializer(payment)
        return Response({
            'message': 'Payment released successfully!',
            'payment': serializer.data
        })


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing feedback.
    """
    queryset = Feedback.objects.all().select_related('client', 'freelancer', 'project').order_by('-submitted_at')
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow anyone to list/retrieve feedback
        Require authentication for other actions
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create feedback with authenticated user as client"""
        serializer.save(client=self.request.user)
    
    def get_queryset(self):
        """Filter feedback based on query parameters"""
        queryset = Feedback.objects.all().select_related('client', 'freelancer', 'project').order_by('-submitted_at')
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by freelancer
        freelancer_id = self.request.query_params.get('freelancer_id', None)
        if freelancer_id:
            queryset = queryset.filter(freelancer_id=freelancer_id)
        
        # Filter by client
        client_id = self.request.query_params.get('client_id', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by rating
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_feedback(self, request):
        """Get all feedback given by the authenticated user"""
        feedback = self.get_queryset().filter(client=request.user)
        page = self.paginate_queryset(feedback)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def received_feedback(self, request):
        """Get all feedback received by the authenticated user (as freelancer)"""
        feedback = self.get_queryset().filter(freelancer=request.user)
        page = self.paginate_queryset(feedback)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)


# API Health Check for Swagger
@swagger_auto_schema(
    method='get',
    operation_description="API Health Check - Check if the API is running",
    responses={200: openapi.Response('API is running successfully')}
)
@api_view(['GET'])
def api_health_check(request):
    """
    Simple API endpoint to check if the API is running.
    This endpoint can be used to test Swagger documentation.
    """
    return Response({
        'status': 'success',
        'message': 'Freelancer API is running successfully!',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat(),
        'authenticated_user': request.user.username if request.user.is_authenticated else 'Anonymous',
        'endpoints': {
            'projects': '/api/project/projects/',
            'proposals': '/api/project/proposals/',
            'milestones': '/api/project/milestones/',
            'payments': '/api/project/payments/',
            'feedbacks': '/api/project/feedbacks/',
        }
    }, status=status.HTTP_200_OK)