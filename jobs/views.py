from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal
from .serializers import (
    JobPostingSerializer, JobApplicationSerializer, JobApplicationUpdateSerializer,
    JobInterviewSerializer, JobOfferSerializer,
    ApplicationWithdrawalSerializer
)

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    #permission_classes = [permissions.IsAuthenticated]  # Add authentication requirement
    
    def create(self, request, *args, **kwargs):
        """POST /api/job-posting - Create job posting"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            from profiles.models import JobProviderProfile
            try:
                # TEMPORARY: For testing, always use the first JobProviderProfile
                job_provider = JobProviderProfile.objects.first()
                if not job_provider:
                    # If no JobProviderProfile exists, create one for testing
                    from django.contrib.auth.models import User
                    test_user, _ = User.objects.get_or_create(username='testuser')
                    job_provider = JobProviderProfile.objects.create(user=test_user)
                
                job = serializer.save(job_provider=job_provider)
                return Response({
                    "job_id": job.id,
                    "message": "Job posted successfully"
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """GET /api/job-posting/{job_id} - Get job posting details"""
        instance = self.get_object()
        return Response({
            "job_id": instance.id,
            "job_title": instance.job_title,
            "department": instance.department,
            "job_type": instance.job_type,
            "work_location": instance.work_location,
            "salary_range": f"{instance.salary_from:,} - {instance.salary_to:,} {instance.currency}",
            "application_deadline": instance.application_deadline.strftime('%Y-%m-%d') if instance.application_deadline else None,
            "interview_mode": instance.interview_mode,
            "hiring_manager": instance.hiring_manager
        })
    
    def list(self, request, *args, **kwargs):
        """GET /api/job-posting - List all job postings"""
        queryset = self.get_queryset()
        
        # Apply filters from query parameters
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(work_location__icontains=location)
        
        job_type = request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type__icontains=job_type)
        
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(job_category__icontains=category)
        
        # Format response
        jobs_list = []
        for job in queryset:
            jobs_list.append({
                "job_id": job.id,
                "job_title": job.job_title,
                "salary_range": f"{job.salary_from:,} - {job.salary_to:,} {job.currency}" if job.salary_from and job.salary_to else "Not specified",
                "location": job.work_location
            })
        
        return Response({"jobs": jobs_list})
    
    def update(self, request, *args, **kwargs):
        """PUT /api/job-posting/{job_id} - Update job posting"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Job posting updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """DELETE /api/job-posting/{job_id} - Delete job posting"""
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Job posting deleted"}, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    Simplified JobApplication ViewSet following the example pattern
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'application_id'
    
    def create(self, request, *args, **kwargs):
        """POST /api/job-application - Apply to job"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get job_id from validated data and remove it
            job_id = serializer.validated_data.pop('job_id')
            
            try:
                job = JobPosting.objects.get(id=job_id)
            except JobPosting.DoesNotExist:
                return Response(
                    {"error": "Job posting not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create the application manually to ensure proper field handling
            application = JobApplication.objects.create(
                job=job,
                freelancer_id=serializer.validated_data['freelancer_id'],
                resume=serializer.validated_data['resume'],
                cover_letter=serializer.validated_data['cover_letter'],
            )
            
            return Response({
                "application_id": application.id,
                "message": "Application submitted successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='job/(?P<job_id>[0-9]+)')
    def get_applications_for_job(self, request, job_id=None):
        """GET /api/job-application/job/{job_id} - Fetch applications for a job"""
        applications = self.queryset.filter(job_id=job_id)
        
        applications_list = []
        for app in applications:
            applications_list.append({
                "application_id": app.id,
                "freelancer_name": f"Freelancer {app.freelancer_id}",  # Simplified
                "resume_url": app.resume,
                "cover_letter_url": app.cover_letter,
                "status": app.status
            })
        
        return Response({"applications": applications_list})
    
    @action(detail=True, methods=['post'], url_path='review')
    def review_application(self, request, application_id=None):
        """POST /api/job-application/review/{application_id} - Review and rate application"""
        application = self.get_object()
        
        rating = request.data.get('rating')
        status_value = request.data.get('status')
        comments = request.data.get('comments')
        
        if rating:
            application.rating = rating
        if status_value:
            application.status = status_value
        if comments:
            application.comments = comments
        
        application.save()
        
        return Response({
            "message": "Application reviewed and rated successfully",
            "application_id": application.id,
            "status": application.status,
            "rating": application.rating,
            "comments": application.comments
        })
    
    @action(detail=True, methods=['put'], url_path='update', serializer_class=JobApplicationUpdateSerializer)
    def update_application_status(self, request, application_id=None):
        """PUT /api/job-application/update/{application_id} - Update application status and rating"""
        application = self.get_object()
        
        # Use the dedicated update serializer for validation
        serializer = JobApplicationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validated data
        status_value = serializer.validated_data.get('status')
        rating = serializer.validated_data.get('rating')
        comments = serializer.validated_data.get('comments')
        
        # Update application with provided data
        if status_value:
            application.status = status_value
        if rating is not None:
            application.rating = rating
        if comments is not None:
            application.comments = comments
        
        application.save()
        
        return Response({
            "message": "Application status and rating updated successfully",
            "application_id": application.id,
            "status": application.status,
            "rating": application.rating,
            "comments": application.comments
        })


class JobInterviewViewSet(viewsets.ModelViewSet):
    """
    Simplified JobInterview ViewSet following the example pattern
    """
    queryset = JobInterview.objects.all()
    serializer_class = JobInterviewSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'interview_id'
    
    @action(detail=False, methods=['post'], url_path='schedule')
    def schedule_interview(self, request):
        """POST /api/job-interview/schedule - Schedule an interview"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get application_id from validated data and remove it
            application_id = serializer.validated_data.pop('application_id')
            
            try:
                application = JobApplication.objects.get(id=application_id)
            except JobApplication.DoesNotExist:
                return Response(
                    {"error": "Job application not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create the interview manually to ensure proper field handling
            interview = JobInterview.objects.create(
                application=application,
                interview_date=serializer.validated_data['interview_date'],
                interview_mode=serializer.validated_data['interview_mode'],
                interview_link=serializer.validated_data.get('interview_link', ''),
                interview_notes=serializer.validated_data.get('interview_notes', ''),
                status='Scheduled'
            )
            
            return Response({
                "interview_id": interview.id,
                "message": "Interview scheduled successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """GET /api/job-interview/{interview_id} - Fetch interview details"""
        instance = self.get_object()
        return Response({
            "interview_id": instance.id,
            "application_id": instance.application.id,
            "date_time": instance.interview_date.strftime('%Y-%m-%dT%H:%M:%SZ') if instance.interview_date else None,
            "interview_mode": instance.interview_mode,
            "interview_link": instance.interview_link,
            "interview_notes": instance.interview_notes
        })
    
    @action(detail=False, methods=['post'], url_path='feedback')
    def provide_feedback(self, request):
        """POST /api/job-interview/feedback - Provide interview feedback"""
        interview_id = request.data.get('interview_id')
        if not interview_id:
            return Response({"error": "interview_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        interview = get_object_or_404(JobInterview, id=interview_id)
        
        rating = request.data.get('rating')
        comments = request.data.get('comments')
        
        if rating:
            interview.rating = rating
        if comments:
            interview.comments = comments
        interview.status = 'Completed'
        interview.save()
        
        return Response({"message": "Feedback submitted successfully"})
    
    @action(detail=False, methods=['post'], url_path='reschedule')
    def reschedule_interview(self, request):
        """POST /api/job-interview/reschedule - Reschedule an interview"""
        interview_id = request.data.get('interview_id')
        if not interview_id:
            return Response({"error": "interview_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        interview = get_object_or_404(JobInterview, id=interview_id)
        
        new_date_time = request.data.get('new_date_time')
        new_interview_link = request.data.get('new_interview_link')
        
        if new_date_time:
            from datetime import datetime
            interview.interview_date = datetime.fromisoformat(new_date_time.replace('Z', '+00:00'))
        if new_interview_link:
            interview.interview_link = new_interview_link
        interview.status = 'Rescheduled'
        interview.save()
        
        return Response({"message": "Interview rescheduled successfully"})


class JobOfferViewSet(viewsets.ModelViewSet):
    """
    Simplified JobOffer ViewSet following the example pattern
    """
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_offer(self, request):
        """POST /api/job-offer/create - Create a job offer"""
        application_id = request.data.get('application_id')
        offer_status = request.data.get('offer_status', 'Pending')
        
        if not application_id:
            return Response(
                {"error": "application_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response(
                {"error": "Job application not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
            # Create the job offer
            offer = JobOffer.objects.create(
                application=application,
                offer_status=offer_status
            )
            
            return Response({
                "offer_id": offer.id,
                "message": "Job offer created successfully"
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='accept')
    def accept_offer(self, request):
        """POST /api/job-offer/accept - Accept a job offer"""
        offer_id = request.data.get('offer_id')
        if not offer_id:
            return Response(
                {"error": "offer_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer = get_object_or_404(JobOffer, id=offer_id)
        offer.offer_status = 'Accepted'
        offer.date_accepted = timezone.now()
        offer.date_rejected = None
        offer.save()
        return Response({'message': 'Job offer accepted'})
    
    @action(detail=False, methods=['post'], url_path='reject')
    def reject_offer(self, request):
        """POST /api/job-offer/reject - Reject a job offer"""
        offer_id = request.data.get('offer_id')
        if not offer_id:
            return Response(
                {"error": "offer_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer = get_object_or_404(JobOffer, id=offer_id)
        offer.offer_status = 'Rejected'
        offer.date_rejected = timezone.now()
        offer.date_accepted = None
        offer.save()
        return Response({'message': 'Job offer rejected'})


class ApplicationWithdrawalViewSet(viewsets.ModelViewSet):
    queryset = ApplicationWithdrawal.objects.all()
    serializer_class = ApplicationWithdrawalSerializer
