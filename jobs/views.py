from django.shortcuts import render
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import JobPosting, JobApplication
from .serializers import JobPostingSerializer, JobApplicationSerializer, JobApplicationListSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobPosting model
    """
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = JobPosting.objects.all()
        
        # Filter by job status
        job_status = self.request.query_params.get('status', None)
        if job_status:
            queryset = queryset.filter(job_status=job_status)
            
        # Filter by job type
        job_type = self.request.query_params.get('type', None)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
            
        # Filter by work mode
        work_mode = self.request.query_params.get('work_mode', None)
        if work_mode:
            queryset = queryset.filter(work_mode=work_mode)
            
        # Filter by job category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(job_category=category)
            
        # Search by title or department
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(job_title__icontains=search) |
                models.Q(department__icontains=search) |
                models.Q(work_location__icontains=search)
            )
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def active_jobs(self, request):
        """
        Get all active job postings
        """
        active_jobs = self.queryset.filter(job_status='open')
        serializer = self.get_serializer(active_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close_job(self, request, pk=None):
        """
        Close a job posting
        """
        job = self.get_object()
        job.job_status = 'closed'
        job.save()
        return Response({'status': 'job closed'})
    
    @action(detail=True, methods=['post'])
    def reopen_job(self, request, pk=None):
        """
        Reopen a closed job posting
        """
        job = self.get_object()
        job.job_status = 'open'
        job.save()
        return Response({'status': 'job reopened'})


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobApplication model
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters and user permissions
        """
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return JobApplication.objects.none()
            
        queryset = JobApplication.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Filter by job
        job_id = self.request.query_params.get('job_id', None)
        if job_id:
            queryset = queryset.filter(job__id=job_id)
            
        # Filter by freelancer (show only user's own applications if they're not staff)
        if not self.request.user.is_staff:
            queryset = queryset.filter(freelancer=self.request.user)
            
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return JobApplicationListSerializer
        return JobApplicationSerializer
    
    def perform_create(self, serializer):
        """
        Set the freelancer to the current user when creating an application
        """
        serializer.save(freelancer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """
        Get current user's job applications
        """
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Response([])
            
        applications = self.queryset.filter(freelancer=request.user)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept_application(self, request, pk=None):
        """
        Accept a job application (for job providers/staff)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        application = self.get_object()
        application.status = 'accepted'
        application.save()
        return Response({'status': 'application accepted'})
    
    @action(detail=True, methods=['post'])
    def reject_application(self, request, pk=None):
        """
        Reject a job application (for job providers/staff)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        application = self.get_object()
        application.status = 'rejected'
        application.save()
        return Response({'status': 'application rejected'})
    
    @action(detail=False, methods=['get'])
    def applications_by_job(self, request):
        """
        Get applications grouped by job (for staff/job providers)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = self.queryset.filter(job__id=job_id)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)