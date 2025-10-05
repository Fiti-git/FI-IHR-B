from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Project, Proposal, Milestone, MilestonePayment, Feedback
from .serializers import (
    ProjectSerializer, ProposalSerializer, MilestoneSerializer,
    MilestonePaymentSerializer, FeedbackSerializer
)


# ==================== PROJECT APIs ====================

@swagger_auto_schema(
    method='get',
    operation_description="Get list of all projects",
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING),
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category", type=openapi.TYPE_STRING),
        openapi.Parameter('employer', openapi.IN_QUERY, description="Filter by employer ID", type=openapi.TYPE_INTEGER),
    ],
    responses={200: ProjectSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new project",
    request_body=ProjectSerializer,
    responses={201: ProjectSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def project_list(request):
    """
    GET: List all projects
    POST: Create new project
    """
    if request.method == 'GET':
        projects = Project.objects.all().order_by('-created_at')
        
        # Filters
        status_filter = request.query_params.get('status')
        category_filter = request.query_params.get('category')
        employer_filter = request.query_params.get('employer')
        
        if status_filter:
            projects = projects.filter(status=status_filter)
        if category_filter:
            projects = projects.filter(category=category_filter)
        if employer_filter:
            projects = projects.filter(employer_id=employer_filter)
        
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Get project details",
    responses={200: ProjectSerializer}
)
@swagger_auto_schema(
    method='put',
    operation_description="Update project",
    request_body=ProjectSerializer,
    responses={200: ProjectSerializer}
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete project",
    responses={204: 'Project deleted successfully'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Changed to AllowAny
def project_detail(request, pk):
    """
    GET: Get single project
    PUT: Update project
    DELETE: Delete project
    """
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        project.delete()
        return Response({'message': 'Project deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='put',
    operation_description="Update project status",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='Project status (open/in_progress/completed)')
        }
    ),
    responses={200: 'Status updated'}
)
@api_view(['PUT'])
@permission_classes([AllowAny])  # Changed to AllowAny
def project_update_status(request, pk):
    """
    PUT: Update project status
    """
    project = get_object_or_404(Project, pk=pk)
    new_status = request.data.get('status')
    
    if new_status not in ['open', 'in_progress', 'completed']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    project.status = new_status
    project.save()
    return Response({'message': 'Status updated', 'status': project.status})


# ==================== PROPOSAL APIs ====================

@swagger_auto_schema(
    method='get',
    operation_description="Get list of all proposals",
    manual_parameters=[
        openapi.Parameter('project_id', openapi.IN_QUERY, description="Filter by project ID", type=openapi.TYPE_INTEGER),
    ],
    responses={200: ProposalSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    operation_description="Submit a new proposal",
    request_body=ProposalSerializer,
    responses={201: ProposalSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def proposal_list(request):
    """
    GET: List all proposals
    POST: Create new proposal
    """
    if request.method == 'GET':
        proposals = Proposal.objects.all().order_by('-submitted_at')
        
        # Filter by project
        project_id = request.query_params.get('project_id')
        if project_id:
            proposals = proposals.filter(project_id=project_id)
        
        serializer = ProposalSerializer(proposals, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProposalSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Get proposal details",
    responses={200: ProposalSerializer}
)
@api_view(['GET'])
@permission_classes([AllowAny])  # Changed to AllowAny
def proposal_detail(request, pk):
    """
    GET: Get single proposal
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    serializer = ProposalSerializer(proposal)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    operation_description="Update proposal status (accept/reject)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='Proposal status (accepted/rejected)')
        }
    ),
    responses={200: 'Proposal status updated'}
)
@api_view(['PUT'])
@permission_classes([AllowAny])  # Changed to AllowAny
def proposal_update_status(request, pk):
    """
    PUT: Update proposal status (accept/reject)
    """
    proposal = get_object_or_404(Proposal, pk=pk)
    new_status = request.data.get('status')
    
    if new_status not in ['accepted', 'rejected']:
        return Response({'error': 'Invalid status. Use "accepted" or "rejected"'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    proposal.status = new_status
    proposal.save()
    
    # If accepted, assign freelancer to project
    if new_status == 'accepted':
        project = proposal.project
        project.freelancer = proposal.freelancer
        project.status = 'in_progress'
        project.save()
    
    return Response({'message': f'Proposal {new_status}', 'status': proposal.status})


# ==================== MILESTONE APIs ====================

@swagger_auto_schema(
    method='get',
    operation_description="Get list of all milestones",
    manual_parameters=[
        openapi.Parameter('project_id', openapi.IN_QUERY, description="Filter by project ID", type=openapi.TYPE_INTEGER),
    ],
    responses={200: MilestoneSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new milestone",
    request_body=MilestoneSerializer,
    responses={201: MilestoneSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def milestone_list(request):
    """
    GET: List all milestones
    POST: Create new milestone
    """
    if request.method == 'GET':
        milestones = Milestone.objects.all().order_by('-created_at')
        
        # Filter by project
        project_id = request.query_params.get('project_id')
        if project_id:
            milestones = milestones.filter(project_id=project_id)
        
        serializer = MilestoneSerializer(milestones, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MilestoneSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Get milestone details",
    responses={200: MilestoneSerializer}
)
@swagger_auto_schema(
    method='put',
    operation_description="Update milestone",
    request_body=MilestoneSerializer,
    responses={200: MilestoneSerializer}
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete milestone",
    responses={204: 'Milestone deleted'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # Changed to AllowAny
def milestone_detail(request, pk):
    """
    GET: Get single milestone
    PUT: Update milestone
    DELETE: Delete milestone
    """
    milestone = get_object_or_404(Milestone, pk=pk)
    
    if request.method == 'GET':
        serializer = MilestoneSerializer(milestone)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MilestoneSerializer(milestone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        milestone.delete()
        return Response({'message': 'Milestone deleted'}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    operation_description="Mark milestone as complete",
    responses={200: 'Milestone marked as completed'}
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def milestone_complete(request, pk):
    """
    POST: Mark milestone as complete
    """
    milestone = get_object_or_404(Milestone, pk=pk)
    milestone.status = 'completed'
    milestone.save()
    return Response({'message': 'Milestone marked as completed', 'status': milestone.status})


# ==================== PAYMENT APIs ====================

@swagger_auto_schema(
    method='get',
    operation_description="Get list of all payments",
    responses={200: MilestonePaymentSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    operation_description="Create payment for milestone",
    request_body=MilestonePaymentSerializer,
    responses={201: MilestonePaymentSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def payment_list(request):
    """
    GET: List all payments
    POST: Create payment for milestone
    """
    if request.method == 'GET':
        payments = MilestonePayment.objects.all().order_by('-created_at')
        serializer = MilestonePaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MilestonePaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            payment.payment_date = timezone.now()
            payment.payment_status = 'completed'
            payment.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Release payment to freelancer",
    responses={200: 'Payment released to freelancer'}
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def payment_release(request, pk):
    """
    POST: Release payment to freelancer
    """
    payment = get_object_or_404(MilestonePayment, pk=pk)
    payment.payment_status = 'released'
    payment.released_at = timezone.now()
    payment.save()
    
    # Update milestone status
    milestone = payment.milestone
    milestone.status = 'approved'
    milestone.save()
    
    return Response({
        'message': 'Payment released to freelancer',
        'payment_status': payment.payment_status,
        'released_at': payment.released_at
    })


# ==================== FEEDBACK APIs ====================

@swagger_auto_schema(
    method='get',
    operation_description="Get list of all feedback",
    manual_parameters=[
        openapi.Parameter('project_id', openapi.IN_QUERY, description="Filter by project ID", type=openapi.TYPE_INTEGER),
    ],
    responses={200: FeedbackSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    operation_description="Submit feedback for a project",
    request_body=FeedbackSerializer,
    responses={201: FeedbackSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Changed to AllowAny
def feedback_list(request):
    """
    GET: List all feedback
    POST: Submit feedback
    """
    if request.method == 'GET':
        feedbacks = Feedback.objects.all().order_by('-submitted_at')
        
        # Filter by project
        project_id = request.query_params.get('project_id')
        if project_id:
            feedbacks = feedbacks.filter(project_id=project_id)
        
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FeedbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Get feedback details",
    responses={200: FeedbackSerializer}
)
@api_view(['GET'])
@permission_classes([AllowAny])  # Changed to AllowAny
def feedback_detail(request, pk):
    """
    GET: Get single feedback
    """
    feedback = get_object_or_404(Feedback, pk=pk)
    serializer = FeedbackSerializer(feedback)
    return Response(serializer.data)