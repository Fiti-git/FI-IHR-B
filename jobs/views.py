from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import models
from .models import JobPosting
from .serializers import JobPostingSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobPosting model - implements the exact APIs requested
    """
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/job-posting/
        Create a new job posting
        """
        # Only accept the exact parameters specified
        allowed_fields = [
            'job_title', 'department', 'job_type', 'work_location', 'role_overview',
            'key_responsibilities', 'required_qualifications', 'preferred_qualifications',
            'languages_required', 'job_category', 'salary_from', 'salary_to', 'currency',
            'application_deadline', 'application_method', 'interview_mode', 'hiring_manager',
            'number_of_openings', 'expected_start_date', 'screening_questions',
            'health_insurance', 'remote_work', 'paid_leave', 'bonus'
        ]
        
        # Filter request data to only include allowed fields
        filtered_data = {key: value for key, value in request.data.items() if key in allowed_fields}
        
        # Set required job_provider_id (default value since not in your parameters)
        filtered_data['job_provider_id'] = 1
        
        serializer = self.get_serializer(data=filtered_data)
        if serializer.is_valid():
            job_posting = serializer.save()
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