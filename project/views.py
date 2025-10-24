from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied

from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag
from .serializers import (
    ProjectSerializer, ProposalSerializer, MilestoneSerializer,
    MilestonePaymentSerializer, FeedbackSerializer, ProjectTagSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects.
    Provides CRUD operations for projects.
    
    List and Retrieve: Anyone can access (AllowAny)
    Create, Update, Delete: Authentication required (IsAuthenticated)
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
        """
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
        """Create proposal with authenticated user as freelancer"""
        serializer.save(freelancer=self.request.user)
    
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
        
        milestone.status = 'completed'
        milestone.save()
        serializer = self.get_serializer(milestone)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a completed milestone - only project owner can approve"""
        milestone = self.get_object()
        
        # Check if user owns the project
        if milestone.project.user != request.user:
            return Response(
                {'error': 'Only project owner can approve milestones'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if milestone.status != 'completed':
            return Response(
                {'error': 'Milestone must be completed before approval'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        milestone.status = 'approved'
        milestone.save()
        serializer = self.get_serializer(milestone)
        return Response(serializer.data)


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
        from django.utils import timezone
        
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
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


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
        'endpoints': {
            'projects': '/api/projects/',
            'proposals': '/api/proposals/',
            'milestones': '/api/milestones/',
            'payments': '/api/payments/',
            'feedbacks': '/api/feedbacks/',
        }
    }, status=status.HTTP_200_OK)