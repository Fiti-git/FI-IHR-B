from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal
from .serializers import (
    JobPostingSerializer, JobApplicationSerializer, JobApplicationUpdateSerializer,
    JobInterviewSerializer, JobOfferSerializer, JobOfferCreateSerializer,
    ApplicationWithdrawalSerializer
)

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    
    def create(self, request, *args, **kwargs):
        """POST /api/job-posting/ - Create job posting"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set job_provider_id automatically (could be from authenticated user or default)
            job = serializer.save(job_provider_id=request.user.id if request.user.is_authenticated else 1)
            return Response({
                "job_id": job.id,
                "message": "Job posted successfully"
            }, status=status.HTTP_201_CREATED)
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
        """GET /api/job-posting/ - List all job postings"""
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
    
    @swagger_auto_schema(
        operation_description="PUT /api/job-posting/- Update job posting",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'job_title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Job title"
                ),
                'salary_from': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Minimum salary"
                ),
                'salary_to': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Maximum salary"
                ),
                'application_deadline': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Application deadline (YYYY-MM-DD)"
                ),
            },
            required=[],  # No required fields - all are optional
        ),
        responses={
            200: openapi.Response(
                description="Job posting updated successfully",
                examples={
                    "application/json": {
                        "message": "Job posting updated",
                        "updated_fields": ["job_title", "salary_from"]
                    }
                }
            ),
            400: "Bad Request",
            404: "Job posting not found"
        }
    )
    def update(self, request, *args, **kwargs):
        """PUT /api/job-posting/{job_id}/ - Update job posting"""
        instance = self.get_object()
        
        # Filter request data to only allow specific fields
        allowed_fields = ['job_title', 'salary_from', 'salary_to', 'application_deadline']
        
        # Update fields directly on the model instance
        updated_fields = []
        for field in allowed_fields:
            if field in request.data:
                setattr(instance, field, request.data[field])
                updated_fields.append(field)
        
        try:
            # Save only the updated fields to avoid validation issues with other fields
            instance.save(update_fields=updated_fields if updated_fields else None)
            return Response({
                "message": "Job posting updated",
                "updated_fields": updated_fields
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """DELETE /api/job-posting/{job_id}/ - Delete job posting"""
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
    
    @swagger_auto_schema(
        operation_description="Submit a job application",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'job_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the job posting to apply for"
                ),
                'freelancer_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the freelancer applying"
                ),
                'resume': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="URL to the freelancer's resume"
                ),
                'cover_letter': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Cover letter text"
                ),
            },
            required=['job_id', 'freelancer_id', 'resume', 'cover_letter'],
        ),
        responses={
            201: openapi.Response(
                description="Application submitted successfully",
                examples={
                    "application/json": {
                        "application_id": 123,
                        "message": "Application submitted successfully"
                    }
                }
            ),
        }
    )
    def create(self, request, *args, **kwargs):
        """POST /api/job-application - Apply to job"""
        
        # Define allowed fields for job application creation
        allowed_fields = ['job_id', 'freelancer_id', 'resume', 'cover_letter']
        
        # Validate that all required fields are present
        missing_fields = [field for field in allowed_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract job_id and validate job exists
        job_id = request.data.get('job_id')
        try:
            job = JobPosting.objects.get(id=job_id)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "Job posting not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Create the application directly using the model
            application = JobApplication.objects.create(
                job=job,
                freelancer_id=request.data['freelancer_id'],
                resume=request.data['resume'],
                cover_letter=request.data['cover_letter'],
                # Set default values for other fields
                status='Pending',
                date_applied=timezone.now()
            )
            
            return Response({
                "application_id": application.id,
                "message": "Application submitted successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
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
                "status": app.status,
                "rating":app.rating,
                "comments": app.comments
            })
        
        return Response({"applications": applications_list})
    
    @swagger_auto_schema(
        operation_description="Review and rate a job application",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rating': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    minimum=1,
                    maximum=5,
                    description="Rating from 1 to 5"
                ),
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['Pending', 'Accepted', 'Rejected', 'Save for Later'],
                    description="Application status"
                ),
                'comments': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Review comments"
                ),
            },
            required=['rating', 'status', 'comments'],
        ),
        responses={
            200: openapi.Response(
                description="Application reviewed successfully",
                examples={
                    "application/json": {
                        "message": "Application reviewed and rated successfully",
                        "application_id": 123,
                        "status": "Accepted",
                        "rating": 4.5,
                        "comments": "Great skills in JavaScript, needs improvement in communication."
                    }
                }
            ),
        }
    )
    @action(detail=True, methods=['post'], url_path='review')
    def review_application(self, request, application_id=None):
        """POST /api/job-application/review/{application_id} - Review and rate application"""
        
        # Define required fields
        required_fields = ['rating', 'status', 'comments']
        
        # Validate that all required fields are present
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the application
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response(
                {"error": "Application not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate rating range
        rating = request.data.get('rating')
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return Response(
                {"error": "Rating must be a number between 1 and 5"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status value
        valid_statuses = ['Pending', 'Accepted', 'Rejected', 'Save for Later']
        status_value = request.data.get('status')
        if status_value not in valid_statuses:
            return Response(
                {"error": f"Status must be one of: {', '.join(valid_statuses)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update application fields directly
            application.rating = rating
            application.status = status_value
            application.comments = request.data.get('comments')
            application.save(update_fields=['rating', 'status', 'comments'])
            
            return Response({
                "message": "Application reviewed and rated successfully",
                "application_id": application.id,
                "status": application.status,
                "rating": float(application.rating),
                "comments": application.comments
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Update application status, rating and comments",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['Pending', 'Accepted', 'Rejected', 'Save for Later'],
                    description="Application status"
                ),
                'rating': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    minimum=1,
                    maximum=5,
                    description="Rating between 1 and 5"
                ),
                'comments': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Comments about the application"
                ),
            },
            required=['status', 'rating', 'comments'],
        ),
        responses={
            200: openapi.Response(
                description="Application updated successfully",
                examples={
                    "application/json": {
                        "message": "Application status and rating updated successfully",
                        "application_id": 123,
                        "status": "Rejected",
                        "rating": 3.5,
                        "comments": "Good technical skills but lacks communication."
                    }
                }
            ),
        }
    )
    @action(detail=True, methods=['put'], url_path='update')
    def update_application_status(self, request, application_id=None):
        """PUT /api/job-application/update/{application_id} - Update application status and rating"""
        
        # Define required fields
        required_fields = ['status', 'rating', 'comments']
        
        # Validate that all required fields are present
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the application
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response(
                {"error": "Application not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate status value
        valid_statuses = ['Pending', 'Accepted', 'Rejected', 'Save for Later']
        status_value = request.data.get('status')
        if status_value not in valid_statuses:
            return Response(
                {"error": f"Status must be one of: {', '.join(valid_statuses)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate rating range
        rating = request.data.get('rating')
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return Response(
                {"error": "Rating must be a number between 1 and 5"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update application fields directly
            application.status = status_value
            application.rating = rating
            application.comments = request.data.get('comments')
            application.save(update_fields=['status', 'rating', 'comments'])
            
            return Response({
                "message": "Application status and rating updated successfully",
                "application_id": application.id,
                "status": application.status,
                "rating": float(application.rating),
                "comments": application.comments
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


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
    
    @swagger_auto_schema(
        operation_description="Provide feedback for a completed interview",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'interview_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the interview to provide feedback for"
                ),
                'rating': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    minimum=1,
                    maximum=5,
                    description="Rating from 1 to 5"
                ),
                'comments': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Feedback comments about the interview"
                ),
            },
            required=['interview_id', 'rating', 'comments'],
        ),
        responses={
            200: openapi.Response(
                description="Feedback submitted successfully",
                examples={
                    "application/json": {
                        "message": "Feedback submitted successfully",
                        "interview_id": 1011,
                        "rating": 4.5,
                        "comments": "Great technical knowledge but needs improvement in communication.",
                        "status": "Completed"
                    }
                }
            ),
        }
    )
    @action(detail=False, methods=['post'], url_path='feedback')
    def provide_feedback(self, request):
        """POST /api/job-interview/feedback - Provide interview feedback"""
        
        # Define required fields
        required_fields = ['interview_id', 'rating', 'comments']
        
        # Validate that all required fields are present
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get interview_id and validate interview exists
        interview_id = request.data.get('interview_id')
        try:
            interview = JobInterview.objects.get(id=interview_id)
        except JobInterview.DoesNotExist:
            return Response(
                {"error": "Interview not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate rating range
        rating = request.data.get('rating')
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return Response(
                {"error": "Rating must be a number between 1 and 5"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update interview fields directly
            interview.rating = rating
            interview.comments = request.data.get('comments')
            interview.status = 'Completed'
            interview.save(update_fields=['rating', 'comments', 'status'])
            
            return Response({
                "message": "Feedback submitted successfully",
                "interview_id": interview.id,
                "rating": float(interview.rating),
                "comments": interview.comments,
                "status": interview.status
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Reschedule an interview with new date/time and link",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'interview_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the interview to reschedule"
                ),
                'new_date_time': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description="New interview date and time (ISO 8601 format)"
                ),
                'new_interview_link': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New interview link (Zoom, Teams, etc.)"
                ),
            },
            required=['interview_id', 'new_date_time', 'new_interview_link'],
        ),
        responses={
            200: openapi.Response(
                description="Interview rescheduled successfully",
                examples={
                    "application/json": {
                        "message": "Interview rescheduled successfully",
                        "interview_id": 1011,
                        "new_date_time": "2025-11-02T10:00:00Z",
                        "new_interview_link": "new_zoom_link",
                        "status": "Rescheduled"
                    }
                }
            ),
            400: "Bad Request - Missing fields or invalid data",
            404: "Interview not found"
        }
    )
    @action(detail=False, methods=['post'], url_path='reschedule')
    def reschedule_interview(self, request):
        """POST /api/job-interview/reschedule - Reschedule an interview"""
        
        # Define required fields
        required_fields = ['interview_id', 'new_date_time', 'new_interview_link']
        
        # Validate that all required fields are present
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get interview_id and validate interview exists
        interview_id = request.data.get('interview_id')
        try:
            interview = JobInterview.objects.get(id=interview_id)
        except JobInterview.DoesNotExist:
            return Response(
                {"error": "Interview not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate and parse new_date_time
        new_date_time = request.data.get('new_date_time')
        try:
            from datetime import datetime
            # Handle ISO 8601 format with Z timezone
            if new_date_time.endswith('Z'):
                parsed_datetime = datetime.fromisoformat(new_date_time.replace('Z', '+00:00'))
            else:
                parsed_datetime = datetime.fromisoformat(new_date_time)
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": "Invalid date format. Use ISO 8601 format (e.g., '2025-11-02T10:00:00Z')"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update interview fields directly
            interview.interview_date = parsed_datetime
            interview.interview_link = request.data.get('new_interview_link')
            interview.status = 'Rescheduled'
            interview.save(update_fields=['interview_date', 'interview_link', 'status'])
            
            return Response({
                "message": "Interview rescheduled successfully",
                "interview_id": interview.id,
                "new_date_time": interview.interview_date.isoformat(),
                "new_interview_link": interview.interview_link,
                "status": interview.status
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class JobOfferViewSet(viewsets.ModelViewSet):
    """
    Simplified JobOffer ViewSet following the example pattern
    """
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    
    @swagger_auto_schema(
        operation_description="Create a job offer for an accepted candidate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'application_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the job application"
                ),
                'offer_details': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'salary': openapi.Schema(
                            type=openapi.TYPE_NUMBER,
                            description="Salary amount"
                        ),
                        'start_date': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATE,
                            description="Start date in YYYY-MM-DD format"
                        ),
                        'benefits': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of benefits"
                        ),
                    },
                    required=['salary', 'start_date', 'benefits'],
                    description="Structured offer details"
                ),
                'offer_status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['Pending', 'Accepted', 'Rejected', 'Withdrawn'],
                    default='Pending',
                    description="Status of the offer"
                ),
            },
            required=['application_id', 'offer_details'],
        ),
        responses={
            201: openapi.Response(
                description="Job offer created successfully",
                examples={
                    "application/json": {
                        "offer_id": 456,
                        "message": "Job offer created successfully",
                        "application_id": 789,
                        "offer_details": {
                            "salary": 70000,
                            "start_date": "2025-11-01",
                            "benefits": ["Health Insurance", "Paid Leave"]
                        },
                        "offer_status": "Pending"
                    }
                }
            ),
        }
    )
    @action(detail=False, methods=['post'], url_path='create')
    def create_offer(self, request):
        """POST /api/job-offer/create - Create a job offer"""
        
        # Use the new serializer for validation
        serializer = JobOfferCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        application_id = validated_data['application_id']
        offer_details = validated_data['offer_details']
        offer_status = validated_data.get('offer_status', 'Pending')
        
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response(
                {"error": "Job application not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if application is in "Accepted" status (business logic)
        if application.status != 'Accepted':
            return Response(
                {"error": "Job offer can only be created for accepted applications"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if an offer already exists for this application
        existing_offer = JobOffer.objects.filter(application=application).first()
        if existing_offer:
            return Response(
                {"error": "A job offer already exists for this application"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            import json
            
            # Format offer_details as a JSON string with proper formatting
            # This will create a string like: {"salary": 70000, "start_date": "2025-11-01", "benefits": ["Health Insurance", "Paid Leave"]}
            formatted_offer_details = json.dumps(offer_details, separators=(',', ': '))
            
            # Create the job offer
            offer = JobOffer.objects.create(
                application=application,
                offer_details=formatted_offer_details,  # Store as formatted JSON string
                offer_status=offer_status
            )
            
            return Response({
                "offer_id": offer.id,
                "message": "Job offer created successfully",
                "application_id": application.id,
                "offer_details": offer_details,
                "offer_status": offer.offer_status
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to create job offer: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def retrieve(self, request, *args, **kwargs):
        """GET /api/job-offer/{offer_id} - Get job offer details"""
        instance = self.get_object()
        
        try:
            import json
            offer_details = json.loads(instance.offer_details) if instance.offer_details else {}
        except (json.JSONDecodeError, TypeError):
            offer_details = {}
        
        return Response({
            "offer_id": instance.id,
            "application_id": instance.application.id,
            "offer_details": offer_details,
            "offer_status": instance.offer_status,
            "date_offered": instance.date_offered.isoformat() if instance.date_offered else None,
            "date_accepted": instance.date_accepted.isoformat() if instance.date_accepted else None,
            "date_rejected": instance.date_rejected.isoformat() if instance.date_rejected else None
        })
    
    @swagger_auto_schema(
        operation_description="Accept a job offer",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'offer_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the job offer to accept"
                ),
            },
            required=['offer_id'],
        ),
        responses={
            200: openapi.Response(
                description="Job offer accepted successfully",
                examples={
                    "application/json": {
                        "message": "Job offer accepted",
                        "offer_id": 456,
                        "offer_status": "Accepted",
                        "date_accepted": "2025-10-06T15:30:00Z"
                    }
                }
            ),
        }
    )
    
    @action(detail=False, methods=['post'], url_path='accept')
    def accept_offer(self, request):
        """POST /api/job-offer/accept - Accept a job offer"""
        offer_id = request.data.get('offer_id')
        if not offer_id:
            return Response(
                {"error": "offer_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            offer = JobOffer.objects.get(id=offer_id)
        except JobOffer.DoesNotExist:
            return Response(
                {"error": "Job offer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        offer.offer_status = 'Accepted'
        offer.date_accepted = timezone.now()
        offer.date_rejected = None
        offer.save()
        
        return Response({
            "message": "Job offer accepted",
            "offer_id": offer.id,
            "offer_status": offer.offer_status,
            "date_accepted": offer.date_accepted.isoformat()
        })
    
    @swagger_auto_schema(
        operation_description="Reject a job offer",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'offer_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the job offer to reject"
                ),
            },
            required=['offer_id'],
        ),
        responses={
            200: openapi.Response(
                description="Job offer rejected successfully",
                examples={
                    "application/json": {
                        "message": "Job offer rejected",
                        "offer_id": 456,
                        "offer_status": "Rejected",
                        "date_rejected": "2025-10-06T15:30:00Z"
                    }
                }
            ),
        }
    )
    @action(detail=False, methods=['post'], url_path='reject')
    def reject_offer(self, request):
        """POST /api/job-offer/reject - Reject a job offer"""
        offer_id = request.data.get('offer_id')
        if not offer_id:
            return Response(
                {"error": "offer_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            offer = JobOffer.objects.get(id=offer_id)
        except JobOffer.DoesNotExist:
            return Response(
                {"error": "Job offer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        offer.offer_status = 'Rejected'
        offer.date_rejected = timezone.now()
        offer.date_accepted = None
        offer.save()
        
        return Response({
            "message": "Job offer rejected",
            "offer_id": offer.id,
            "offer_status": offer.offer_status,
            "date_rejected": offer.date_rejected.isoformat()
        })


class ApplicationWithdrawalViewSet(viewsets.ModelViewSet):
    queryset = ApplicationWithdrawal.objects.all()
    serializer_class = ApplicationWithdrawalSerializer
