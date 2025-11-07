from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal
from .serializers import (
    JobPostingSerializer, JobApplicationSerializer, JobApplicationUpdateSerializer,
    JobInterviewSerializer, JobOfferSerializer, JobOfferCreateSerializer,
    ApplicationWithdrawalSerializer
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from profiles.models import FreelancerProfile

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    permission_classes = [permissions.IsAuthenticated]  # default; overridden per action below

    def get_permissions(self):
        """Allow public access to list/retrieve; require auth for mutations."""
        if getattr(self, 'action', None) in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """POST /api/job-posting - Create job posting"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            from profiles.models import JobProviderProfile
            try:
                job_provider = JobProviderProfile.objects.filter(user=request.user).first()
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
            "work_mode": instance.work_mode,
            "role_overview": instance.role_overview,
            "key_responsibilities": instance.key_responsibilities,
            "required_qualifications": instance.required_qualifications,
            "preferred_qualifications": instance.preferred_qualifications,
            "language_required": instance.languages_required,
            "category": instance.job_category,
            "salary_from": instance.salary_from,
            "salary_to": instance.salary_to,
            "currency": instance.currency,
            "application_deadline": instance.application_deadline.strftime('%Y-%m-%d') if instance.application_deadline else None,
            "interview_mode": instance.interview_mode,
            "hiring_manager": instance.hiring_manager,
            "number_of_openings": instance.number_of_openings,
            "expected_start_date": instance.expected_start_date.strftime('%Y-%m-%d') if instance.expected_start_date else None,
            "screening_questions": instance.screening_questions,
            "health_insurance": instance.health_insurance,
            "remote_work": instance.remote_work,
            "paid_leave": instance.paid_leave,
            "bonus": instance.bonus,
            "date_posted": instance.date_posted.strftime('%Y-%m-%d') if instance.date_posted else None,
            "job_status": instance.job_status,
            

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
                "location": job.work_location,
                "date_posted": job.date_posted.strftime('%Y-%m-%d') if job.date_posted else None,
                "job_status": job.job_status,
                "job_category": job.job_category
            })
        
        return Response({"jobs": jobs_list})

    @action(detail=False, methods=['get'], url_path='job-manage')
    def job_manage(self, request):
        """GET /api/job-posting/job-manage?job_provider_id=ID - Return all jobs, applications, interviews and offers for a job provider"""
        job_provider_id = request.query_params.get('job_provider_id') or request.query_params.get('provider_id')

        # If not provided, try to infer from authenticated user's JobProviderProfile
        if not job_provider_id and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            try:
                from profiles.models import JobProviderProfile
                profile = JobProviderProfile.objects.filter(user=request.user).first()
                if profile:
                    job_provider_id = profile.id
            except Exception:
                pass

        if not job_provider_id:
            return Response({"error": "job_provider_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Collect jobs for this provider
        jobs_qs = JobPosting.objects.filter(job_provider_id=job_provider_id)

        result_jobs = []
        for job in jobs_qs:
            job_dict = {
                "job_id": job.id,
                "job_title": job.job_title,
                "department": job.department,
                "job_type": job.job_type,
                "work_location": job.work_location,
                "work_mode": job.work_mode,
                "role_overview": job.role_overview,
                "key_responsibilities": job.key_responsibilities,
                "required_qualifications": job.required_qualifications,
                "preferred_qualifications": job.preferred_qualifications,
                "languages_required": job.languages_required,
                "job_category": job.job_category,
                "salary_from": job.salary_from,
                "salary_to": job.salary_to,
                "currency": job.currency,
                "application_deadline": job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else None,
                "interview_mode": job.interview_mode,
                "hiring_manager": job.hiring_manager,
                "number_of_openings": job.number_of_openings,
                "expected_start_date": job.expected_start_date.strftime('%Y-%m-%d') if job.expected_start_date else None,
                "screening_questions": job.screening_questions,
                "file_upload": job.file_upload,
                "health_insurance": job.health_insurance,
                "remote_work": job.remote_work,
                "paid_leave": job.paid_leave,
                "bonus": job.bonus,
                "date_posted": job.date_posted.strftime('%Y-%m-%d %H:%M:%S') if job.date_posted else None,
                "job_status": job.job_status,
            }

            # Applications for this job
            applications_qs = JobApplication.objects.filter(job=job)
            applications_list = []
            for app in applications_qs:
                app_dict = {
                    "application_id": app.id,
                    "freelancer_id": app.freelancer_id,
                    "resume": app.resume,
                    "cover_letter": app.cover_letter,
                    "expected_rate": app.expected_rate,
                    "status": app.status,
                    "date_applied": app.date_applied.strftime('%Y-%m-%d %H:%M:%S') if app.date_applied else None,
                    "rating": app.rating,
                    "comments": app.comments,
                }

                # Interviews for this application
                interviews_qs = JobInterview.objects.filter(application=app)
                interviews_list = []
                for iv in interviews_qs:
                    interviews_list.append({
                        "interview_id": iv.id,
                        "interview_date": iv.interview_date.strftime('%Y-%m-%d %H:%M:%S') if iv.interview_date else None,
                        "interview_mode": iv.interview_mode,
                        "status": iv.status,
                        "interview_link": iv.interview_link,
                        "interview_notes": iv.interview_notes,
                        "rating": iv.rating,
                        "comments": iv.comments,
                    })

                # Offers for this application
                offers_qs = JobOffer.objects.filter(application=app)
                offers_list = []
                for of in offers_qs:
                    offers_list.append({
                        "offer_id": of.id,
                        "offer_status": of.offer_status,
                        "offer_details": of.offer_details,
                        "date_offered": of.date_offered.strftime('%Y-%m-%d %H:%M:%S') if of.date_offered else None,
                        "date_accepted": of.date_accepted.strftime('%Y-%m-%d %H:%M:%S') if of.date_accepted else None,
                        "date_rejected": of.date_rejected.strftime('%Y-%m-%d %H:%M:%S') if of.date_rejected else None,
                    })

                app_dict['interviews'] = interviews_list
                app_dict['offers'] = offers_list

                applications_list.append(app_dict)

            job_dict['applications'] = applications_list

            result_jobs.append(job_dict)

        return Response({"job_provider_id": job_provider_id, "jobs": result_jobs})
    
    def update(self, request, *args, **kwargs):
        """PUT /api/job-posting/{job_id} - Update job posting"""
        partial = kwargs.pop('partial', False)
        # Require job_status to be provided for updates
        if 'job_status' not in request.data:
            return Response({"error": "job_status is required for update"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND)

            # Create the application manually to ensure proper field handling
            application = JobApplication.objects.create(
                job=job,
                freelancer_id=serializer.validated_data.get('freelancer_id'),
                resume=serializer.validated_data.get('resume'),
                cover_letter=serializer.validated_data.get('cover_letter'),
                expected_rate=serializer.validated_data.get('expected_rate')
            )
            
            return Response({
                "application_id": application.id,
                "message": "Application submitted successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=False, methods=['get'], url_path='job/(?P<job_id>[0-9]+)')
    # def get_applications_for_job(self, request, job_id=None):
    #     """GET /api/job-application/job/{job_id} - Fetch applications for a job"""
    #     applications = self.queryset.filter(job_id=job_id)
        
    #     applications_list = []
    #     for app in applications:
    #         # Try to resolve freelancer name from profiles.FreelancerProfile if available
    #         try:
    #             from profiles.models import FreelancerProfile
    #             profile = FreelancerProfile.objects.filter(id=app.freelancer_id).select_related('user').first()
    #             if profile:
    #                 freelancer_name = profile.full_name or (profile.user.username if profile.user else f"Freelancer {app.freelancer_id}")
    #             else:
    #                 freelancer_name = f"Freelancer {app.freelancer_id}"
    #         except Exception:
    #             # Fall back to the numeric id if any error occurs
    #             freelancer_name = f"Freelancer {app.freelancer_id}"

    #         applications_list.append({
    #             "application_id": app.id,
    #             "freelance_id": app.freelancer_id,
    #             "freelancer_name": freelancer_name,
    #             "resume_url": app.resume,
    #             "cover_letter_url": app.cover_letter,
    #             "status": app.status,
    #             "rating": app.rating
    #         })
        
    #     return Response({"applications": applications_list})

    @action(detail=False, methods=['get'], url_path=r'job/(?P<job_id>[0-9]+)')
    def get_applications_for_job(self, request, job_id=None):
        """GET /api/job-application/job/{job_id} - Fetch applications for a job"""
        applications = self.queryset.filter(job_id=job_id)
        applications_list = []

        # Fetch the job posting & employer user id
        job_posting = JobPosting.objects.select_related('job_provider').filter(id=job_id).first()
        employer_user_id = None
        if job_posting and job_posting.job_provider:
            # job_provider = JobProviderProfile
            employer_user_id = job_posting.job_provider.user_id

        for app in applications:
            # Get freelancer profile and name
            profile = FreelancerProfile.objects.select_related('user').filter(user_id=app.freelancer_id).first()
            if profile:
                freelancer_name = (
                    profile.full_name
                    or (profile.user.username if profile.user else f"Freelancer {app.freelancer_id}")
                )
                freelancer_user_id = profile.user_id
            else:
                freelancer_name = f"Freelancer {app.freelancer_id}"
                freelancer_user_id = app.freelancer_id  # fallback (since freelancer_id = auth_user_id)

            # Add each application entry
            applications_list.append({
                "application_id": app.id,
                "freelancer_id": app.freelancer_id,
                "freelancer_user_id": freelancer_user_id,
                "freelancer_name": freelancer_name,
                "employer_user_id": employer_user_id,
                "resume_url": app.resume,
                "cover_letter_url": app.cover_letter,
                "status": app.status,
                "rating": app.rating,
                "chat_users": [freelancer_user_id, employer_user_id] if employer_user_id else [freelancer_user_id],
            })

        return Response({"applications": applications_list})
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
            job_id = serializer.validated_data.get('job_id')
            freelance_id = serializer.validated_data.get('freelance_id')
            
            try:
                application = JobApplication.objects.get(id=application_id)
            except JobApplication.DoesNotExist:
                return Response(
                    {"error": "Job application not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Validate provided job_id and freelance_id match the application
            if not job_id or not freelance_id:
                return Response(
                    {"error": "job_id and freelance_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if int(job_id) != int(application.job_id) or int(freelance_id) != int(application.freelancer_id):
                return Response(
                    {"error": "job_id or freelance_id does not match the application"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the interview manually to ensure proper field handling
            interview = JobInterview.objects.create(
                application=application,
                # Populate new denormalized fields for convenience/queries
                job=application.job,
                freelancer_id=application.freelancer_id,
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

    @action(detail=False, methods=['get'], url_path='application/(?P<application_id>[0-9]+)')
    def get_by_application(self, request, application_id=None):
        """GET /api/job-interview/application/{application_id} - Return latest interview status and link for an application"""
        interviews = JobInterview.objects.filter(application_id=application_id)
        if not interviews.exists():
            return Response({"error": "Interview not found for the given application_id"}, status=status.HTTP_404_NOT_FOUND)

        # Return the most recent interview (by interview_date)
        interview = interviews.order_by('-interview_date').first()
        return Response({
            "application_id": application_id,
            "status": interview.status,
            "interview_link": interview.interview_link,
            "interview_date": interview.interview_date.strftime('%Y-%m-%dT%H:%M:%SZ') if interview.interview_date else None,
            "interview_mode": interview.interview_mode,
            "interview_notes": interview.interview_notes
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
    
    @swagger_auto_schema(request_body=JobOfferCreateSerializer, responses={201: JobOfferSerializer()})
    @action(detail=False, methods=['post'], url_path='create')
    def create_offer(self, request):
        """POST /api/job-offer/create - Create a job offer"""
        # Validate input using JobOfferCreateSerializer so Swagger shows fields
        serializer = JobOfferCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        application_id = validated.get('application_id')
        offer_status = validated.get('offer_status', 'Pending')
        offer_details = validated.get('offer_details')

        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Job application not found"}, status=status.HTTP_404_NOT_FOUND)

        # store offer_details as JSON string in the TextField
        import json
        offer_details_text = json.dumps(offer_details)

        offer = JobOffer.objects.create(
            application=application,
            offer_status=offer_status,
            offer_details=offer_details_text
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_jobs_for_freelancer(request, freelance_id):
    """GET /api/freelance/{freelance_id} - Return jobs related to a freelancer.

    Response: list of jobs with fields: job_id, job_title, job_category, date_posted, job_status
    """
    # Find applications by this freelancer id
    applications = JobApplication.objects.filter(freelancer_id=freelance_id).select_related('job')

    jobs_map = {}
    for app in applications:
        job = app.job
        if job and job.id not in jobs_map:
            jobs_map[job.id] = {
                "job_id": job.id,
                "job_title": job.job_title,
                "job_category": job.job_category,
                "date_posted": job.date_posted.strftime('%Y-%m-%d') if job.date_posted else None,
                "job_status": job.job_status,
            }

    jobs_list = list(jobs_map.values())

    return Response({"freelance_id": freelance_id, "jobs": jobs_list})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_interviews_by_job(request, job_id):
    """GET /api/interview/{job_id} - Return interviews for a job, filtered by access token

    Response: { "interviews": [ {interview_date, interview_mode, status, interview_notes}, ... ] }
    Filtering rules:
      - If the user is a Freelancer (has FreelancerProfile), only return interviews where freelancer_id matches their profile id
      - If the user is a Job Provider (has JobProviderProfile), only return interviews for jobs owned by that provider
      - Otherwise, default to no data (empty list)
    """
    interviews_qs = JobInterview.objects.filter(job_id=job_id)

    try:
        from profiles.models import FreelancerProfile, JobProviderProfile

        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            # Check for freelancer role
            freelancer_profile = FreelancerProfile.objects.filter(user=request.user).first()
            if freelancer_profile:
                interviews_qs = interviews_qs.filter(freelancer_id=freelancer_profile.id)
            else:
                # Check for job provider role
                provider_profile = JobProviderProfile.objects.filter(user=request.user).first()
                if provider_profile:
                    interviews_qs = interviews_qs.filter(job__job_provider=provider_profile)
                else:
                    # Authenticated but no matching role; return empty
                    interviews_qs = interviews_qs.none()
    except Exception:
        # On any error resolving profiles, return empty to avoid leaking data
        interviews_qs = interviews_qs.none()

    interviews_list = []
    for iv in interviews_qs.order_by('-interview_date'):
        interviews_list.append({
            "interview_date": iv.interview_date.strftime('%Y-%m-%dT%H:%M:%SZ') if iv.interview_date else None,
            "interview_mode": iv.interview_mode,
            "status": iv.status,
            "interview_notes": iv.interview_notes,
            "interview_link": iv.interview_link,
        })

    return Response({"interviews": interviews_list})
