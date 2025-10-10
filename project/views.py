from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny  # Add AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User

from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag
from .serializers import (
    ProjectSerializer, ProposalSerializer, MilestoneSerializer,
    MilestonePaymentSerializer, FeedbackSerializer, ProjectTagSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects.
    Provides CRUD operations for projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]  # Change this line
    
    # TODO: Restore authentication after testing
    """
    def get_permissions(self):
        # Instantiates and returns the list of permissions that this view requires.
        # - Allow anyone to list and retrieve projects
        # - Require authentication for create, update, delete
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    """
    
    from django.contrib.auth.models import User

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Create project with user handling"""
        try:
            # Check if user is authenticated
            if self.request.user and self.request.user.is_authenticated:
                serializer.save(user=self.request.user)
            else:
                # For testing: get or create a default user
                user, created = User.objects.get_or_create(
                    username='default_user',
                    defaults={
                        'email': 'default@example.com',
                        'first_name': 'Default',
                        'last_name': 'User'
                    }
                )
                if created:
                    user.set_password('password123')
                    user.save()
                    print(f"Created default user: {user.username}")
                
                serializer.save(user=user)
                print(f"Project created with user: {user.username}")
                
        except Exception as e:
            print(f"Error in perform_create: {str(e)}")
            raise
    
    def get_queryset(self):
        queryset = Project.objects.all()
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
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """Add a tag to a project"""
        project = self.get_object()
        tag_name = request.data.get('tag')
        
        if not tag_name:
            return Response({'error': 'Tag name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        tag, created = ProjectTag.objects.get_or_create(project=project, tag=tag_name)
        serializer = ProjectTagSerializer(tag)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ProposalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing proposals.
    Freelancers can submit proposals for projects.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Proposal.objects.all()
        
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
    
    @action(detail=True, methods=['patch'])
    def accept(self, request, pk=None):
        """Accept a proposal"""
        proposal = self.get_object()
        proposal.status = 'accepted'
        proposal.save()
        serializer = self.get_serializer(proposal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Reject a proposal"""
        proposal = self.get_object()
        proposal.status = 'rejected'
        proposal.save()
        serializer = self.get_serializer(proposal)
        return Response(serializer.data)


class MilestoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing milestones.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Milestone.objects.all()
        
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
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """Mark milestone as completed"""
        milestone = self.get_object()
        milestone.status = 'completed'
        milestone.save()
        serializer = self.get_serializer(milestone)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve a completed milestone"""
        milestone = self.get_object()
        milestone.status = 'approved'
        milestone.save()
        serializer = self.get_serializer(milestone)
        return Response(serializer.data)


class MilestonePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing milestone payments.
    """
    queryset = MilestonePayment.objects.all()
    serializer_class = MilestonePaymentSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = MilestonePayment.objects.all()
        
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
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def release_payment(self, request, pk=None):
        """Release payment to freelancer"""
        from django.utils import timezone
        
        payment = self.get_object()
        payment.payment_status = 'released'
        payment.released_at = timezone.now()
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing feedback.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Feedback.objects.all()
        
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
        
        return queryset


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
        'endpoints': {
            'projects': '/api/projects/',
            'proposals': '/api/proposals/',
            'milestones': '/api/milestones/',
            'payments': '/api/payments/',
            'feedbacks': '/api/feedbacks/',
        }
    }, status=status.HTTP_200_OK)