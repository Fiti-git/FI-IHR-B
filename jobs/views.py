from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.shortcuts import get_object_or_404
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal
from .serializers import (
    JobPostingSerializer, JobPostingCreateSerializer, JobApplicationSerializer, 
    JobApplicationCreateSerializer, JobApplicationJobListSerializer, 
    JobApplicationReviewSerializer, JobApplicationUpdateSerializer,
    JobInterviewSerializer, JobOfferSerializer, ApplicationWithdrawalSerializer
)


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobPosting model - implements the exact APIs requested
    """
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action
        """
        if self.action == 'create':
            return JobPostingCreateSerializer
        return JobPostingSerializer
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/job-posting/
        Create a new job posting
        """
        # Use the create serializer which excludes job_provider_id and work_mode
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set default values for excluded fields
            job_posting = serializer.save(
                job_provider_id=1,  # Set default value since not in request
                work_mode='on-site'  # Set default value since not in request
            )
            # Return EXACTLY the specified response format - nothing else
            return Response({
                "job_id": job_posting.id,
                "message": "Job posted successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            # Return validation errors if any
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/job-posting/{job_id}/
        Fetch a specific job posting by its ID
        """
        instance = self.get_object()
        
        # Create custom salary range since we removed the property
        if instance.salary_from and instance.salary_to:
            salary_range = f"{instance.currency} {instance.salary_from:,.0f} - {instance.salary_to:,.0f}"
        elif instance.salary_from:
            salary_range = f"{instance.currency} {instance.salary_from:,.0f}+"
        else:
            salary_range = "Salary not specified"
        
        # Return exactly the specified response format
        response_data = {
            "job_id": instance.id,
            "job_title": instance.job_title,
            "department": instance.department,
            "job_type": instance.job_type,
            "work_location": instance.work_location,
            "salary_range": salary_range,
            "application_deadline": instance.application_deadline.strftime('%Y-%m-%d') if instance.application_deadline else None,
            "interview_mode": instance.interview_mode,
            "hiring_manager": instance.hiring_manager
        }
        
        return Response(response_data)
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/job-posting/
        Fetch a list of all job postings with optional filtering
        """
        queryset = self.get_queryset()
        
        # Apply filters based on query parameters
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(work_location__icontains=location)
        
        job_type = request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type__iexact=job_type)
        
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(job_category__icontains=category)
        
        salary_range = request.query_params.get('salary_range')
        if salary_range and '-' in salary_range:
            try:
                min_salary, max_salary = salary_range.split('-')
                min_salary = float(min_salary)
                max_salary = float(max_salary)
                queryset = queryset.filter(
                    salary_from__gte=min_salary,
                    salary_to__lte=max_salary
                )
            except (ValueError, TypeError):
                pass  # Ignore invalid salary range format
        
        # Format response data
        jobs_list = []
        for job in queryset:
            # Create custom salary range for each job
            if job.salary_from and job.salary_to:
                job_salary_range = f"{job.currency} {job.salary_from:,.0f} - {job.salary_to:,.0f}"
            elif job.salary_from:
                job_salary_range = f"{job.currency} {job.salary_from:,.0f}+"
            else:
                job_salary_range = "Salary not specified"
                
            jobs_list.append({
                "job_id": job.id,
                "job_title": job.job_title,
                "salary_range": job_salary_range,
                "location": job.work_location
            })
        
        return Response({
            "jobs": jobs_list
        })
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/job-posting/{job_id}/
        Update an existing job post
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Job posting updated"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/job-posting/{job_id}/
        Partially update an existing job post
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/job-posting/{job_id}/
        Delete a job posting by its ID
        """
        instance = self.get_object()
        instance.delete()
        
        return Response({
            "message": "Job posting deleted"
        }, status=status.HTTP_200_OK)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobApplication model - provides CRUD operations for job applications
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action
        """
        if self.action == 'create':
            return JobApplicationCreateSerializer
        elif self.action == 'get_applications_for_job':
            return JobApplicationJobListSerializer
        elif self.action == 'review_application':
            return JobApplicationReviewSerializer
        elif self.action == 'update_application_status':
            return JobApplicationUpdateSerializer
        return JobApplicationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/job-application/
        Create a new job application
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            application = serializer.save()
            return Response({
                "application_id": application.id,
                "message": "Application submitted successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_applications_for_job(self, request, job_id=None):
        """
        GET /api/job-application/job/{job_id}/
        Fetch all applications for a specific job
        """
        # Get all applications for the specified job
        applications = JobApplication.objects.filter(job_id=job_id)
        
        if not applications.exists():
            return Response({
                "applications": []
            })
        
        serializer = self.get_serializer(applications, many=True)
        return Response({
            "applications": serializer.data
        })
    
    def review_application(self, request, application_id=None):
        """
        POST /api/job-application/review/{application_id}/
        Review and rate an application
        """
        application = get_object_or_404(JobApplication, id=application_id)
        serializer = self.get_serializer(application, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Application reviewed and rated successfully",
                "application_id": application.id,
                "status": application.status,
                "rating": application.rating,
                "comments": application.comments
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_application_status(self, request, application_id=None):
        """
        PUT /api/job-application/update/{application_id}/
        Update application status and rating
        """
        application = get_object_or_404(JobApplication, id=application_id)
        serializer = self.get_serializer(application, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Application status and rating updated successfully",
                "application_id": application.id,
                "status": application.status,
                "rating": application.rating,
                "comments": application.comments
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/job-application/{id}/
        Fetch a specific job application by its ID
        """
        instance = self.get_object()
        
        response_data = {
            "application_id": instance.id,
            "job_id": instance.job.id,
            "job_title": instance.job.job_title,
            "freelancer_id": instance.freelancer_id,
            "resume": instance.resume,
            "cover_letter": instance.cover_letter,
            "expected_rate": str(instance.expected_rate),
            "status": instance.status,
            "date_applied": instance.date_applied.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return Response(response_data)
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/job-application/
        Fetch a list of all job applications with optional filtering
        """
        queryset = self.get_queryset()
        
        # Apply filters based on query parameters
        job_id = request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        freelancer_id = request.query_params.get('freelancer_id')
        if freelancer_id:
            queryset = queryset.filter(freelancer_id=freelancer_id)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        
        # Format response data
        applications_list = []
        for app in queryset:
            applications_list.append({
                "application_id": app.id,
                "job_id": app.job.id,
                "job_title": app.job.job_title,
                "freelancer_id": app.freelancer_id,
                "status": app.status,
                "expected_rate": str(app.expected_rate),
                "date_applied": app.date_applied.strftime('%Y-%m-%d')
            })
        
        return Response({
            "applications": applications_list
        })
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/job-application/{id}/
        Update an existing job application
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Job application updated"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/job-application/{id}/
        Partially update an existing job application
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/job-application/{id}/
        Delete a job application by its ID
        """
        instance = self.get_object()
        instance.delete()
        
        return Response({
            "message": "Job application deleted"
        }, status=status.HTTP_200_OK)


class JobInterviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobInterview model - provides CRUD operations for job interviews
    """
    queryset = JobInterview.objects.all()
    serializer_class = JobInterviewSerializer
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/job-interview/
        Create a new job interview
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            interview = serializer.save()
            return Response({
                "interview_id": interview.id,
                "message": "Interview scheduled successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/job-interview/{id}/
        Fetch a specific job interview by its ID
        """
        instance = self.get_object()
        
        response_data = {
            "interview_id": instance.id,
            "application_id": instance.application.id,
            "interview_date": instance.interview_date.strftime('%Y-%m-%d %H:%M:%S'),
            "interview_mode": instance.interview_mode,
            "status": instance.status,
            "interview_notes": instance.interview_notes
        }
        
        return Response(response_data)
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/job-interview/
        Fetch a list of all job interviews with optional filtering
        """
        queryset = self.get_queryset()
        
        # Apply filters based on query parameters
        application_id = request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        
        freelancer_id = request.query_params.get('freelancer_id')
        if freelancer_id:
            queryset = queryset.filter(application__freelancer_id=freelancer_id)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        
        interview_mode = request.query_params.get('interview_mode')
        if interview_mode:
            queryset = queryset.filter(interview_mode__iexact=interview_mode)
        
        # Format response data
        interviews_list = []
        for interview in queryset:
            interviews_list.append({
                "interview_id": interview.id,
                "application_id": interview.application.id,
                "interview_date": interview.interview_date.strftime('%Y-%m-%d %H:%M'),
                "interview_mode": interview.interview_mode,
                "status": interview.status
            })
        
        return Response({
            "interviews": interviews_list
        })
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/job-interview/{id}/
        Update an existing job interview
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Job interview updated"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/job-interview/{id}/
        Partially update an existing job interview
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/job-interview/{id}/
        Delete a job interview by its ID
        """
        instance = self.get_object()
        instance.delete()
        
        return Response({
            "message": "Job interview deleted"
        }, status=status.HTTP_200_OK)


class JobOfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobOffer model - provides CRUD operations for job offers
    """
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/job-offer/
        Create a new job offer
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
            return Response({
                "offer_id": offer.id,
                "message": "Job offer created successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/job-offer/{id}/
        Fetch a specific job offer by its ID
        """
        instance = self.get_object()
        
        response_data = {
            "offer_id": instance.id,
            "application_id": instance.application.id,
            "offer_status": instance.offer_status,
            "offer_details": instance.offer_details,
            "date_offered": instance.date_offered.strftime('%Y-%m-%d %H:%M:%S'),
            "date_accepted": instance.date_accepted.strftime('%Y-%m-%d %H:%M:%S') if instance.date_accepted else None,
            "date_rejected": instance.date_rejected.strftime('%Y-%m-%d %H:%M:%S') if instance.date_rejected else None
        }
        
        return Response(response_data)
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/job-offer/
        Fetch a list of all job offers with optional filtering
        """
        queryset = self.get_queryset()
        
        # Apply filters based on query parameters
        application_id = request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        
        freelancer_id = request.query_params.get('freelancer_id')
        if freelancer_id:
            queryset = queryset.filter(application__freelancer_id=freelancer_id)
        
        status_filter = request.query_params.get('offer_status')
        if status_filter:
            queryset = queryset.filter(offer_status__iexact=status_filter)
        
        # Format response data
        offers_list = []
        for offer in queryset:
            offers_list.append({
                "offer_id": offer.id,
                "application_id": offer.application.id,
                "offer_status": offer.offer_status,
                "date_offered": offer.date_offered.strftime('%Y-%m-%d %H:%M')
            })
        
        return Response({
            "offers": offers_list
        })
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/job-offer/{id}/
        Update an existing job offer
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Job offer updated"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/job-offer/{id}/
        Partially update an existing job offer
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/job-offer/{id}/
        Delete a job offer by its ID
        """
        instance = self.get_object()
        instance.delete()
        
        return Response({
            "message": "Job offer deleted"
        }, status=status.HTTP_200_OK)


class ApplicationWithdrawalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ApplicationWithdrawal model - provides CRUD operations for application withdrawals
    """
    queryset = ApplicationWithdrawal.objects.all()
    serializer_class = ApplicationWithdrawalSerializer
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/application-withdrawal/
        Create a new application withdrawal
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            withdrawal = serializer.save()
            return Response({
                "withdrawal_id": withdrawal.id,
                "message": "Application withdrawn successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/application-withdrawal/{id}/
        Fetch a specific application withdrawal by its ID
        """
        instance = self.get_object()
        
        response_data = {
            "withdrawal_id": instance.id,
            "application_id": instance.application.id,
            "withdrawal_date": instance.withdrawal_date.strftime('%Y-%m-%d %H:%M:%S'),
            "reason": instance.reason
        }
        
        return Response(response_data)
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/application-withdrawal/
        Fetch a list of all application withdrawals with optional filtering
        """
        queryset = self.get_queryset()
        
        # Apply filters based on query parameters
        application_id = request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        
        freelancer_id = request.query_params.get('freelancer_id')
        if freelancer_id:
            queryset = queryset.filter(application__freelancer_id=freelancer_id)
        
        # Format response data
        withdrawals_list = []
        for withdrawal in queryset:
            withdrawals_list.append({
                "withdrawal_id": withdrawal.id,
                "application_id": withdrawal.application.id,
                "withdrawal_date": withdrawal.withdrawal_date.strftime('%Y-%m-%d %H:%M')
            })
        
        return Response({
            "withdrawals": withdrawals_list
        })
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/application-withdrawal/{id}/
        Update an existing application withdrawal (only reason can be updated)
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Only allow updating the reason field
        allowed_fields = ['reason']
        filtered_data = {key: value for key, value in request.data.items() if key in allowed_fields}
        
        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Application withdrawal updated"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/application-withdrawal/{id}/
        Partially update an existing application withdrawal
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/application-withdrawal/{id}/
        Delete an application withdrawal (this will restore the application status)
        """
        instance = self.get_object()
        
        # Restore the application status to Pending when withdrawal is deleted
        application = instance.application
        application.status = 'Pending'
        application.save()
        
        instance.delete()
        
        return Response({
            "message": "Application withdrawal deleted and application status restored"
        }, status=status.HTTP_200_OK)