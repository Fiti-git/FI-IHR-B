from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import JobPosting, JobApplication


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for JobPosting model
    """
    salary_range = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ['date_posted', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate salary range and application deadline
        """
        # Validate salary range
        salary_from = data.get('salary_from')
        salary_to = data.get('salary_to')
        
        if salary_from and salary_to and salary_from > salary_to:
            raise serializers.ValidationError(
                "Minimum salary cannot be greater than maximum salary."
            )
        
        # Validate application deadline
        application_deadline = data.get('application_deadline')
        if application_deadline and application_deadline < timezone.now():
            raise serializers.ValidationError(
                "Application deadline cannot be in the past."
            )
        
        # Validate expected start date
        expected_start_date = data.get('expected_start_date')
        if expected_start_date and expected_start_date < timezone.now():
            raise serializers.ValidationError(
                "Expected start date cannot be in the past."
            )
        
        return data


class JobPostingListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing job postings
    """
    salary_range = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'job_title', 'department', 'job_type', 'work_location',
            'work_mode', 'job_category', 'salary_range', 'application_deadline',
            'number_of_openings', 'job_status', 'date_posted', 'is_active'
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for JobApplication model
    """
    # Read-only fields for nested object representation
    freelancer_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    is_pending = serializers.ReadOnlyField()
    is_accepted = serializers.ReadOnlyField()
    is_rejected = serializers.ReadOnlyField()
    
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['date_applied']
    
    def get_freelancer_name(self, obj):
        """Get freelancer's full name or username"""
        if obj.freelancer.first_name and obj.freelancer.last_name:
            return f"{obj.freelancer.first_name} {obj.freelancer.last_name}"
        return obj.freelancer.username
    
    def get_job_title(self, obj):
        """Get the job title"""
        return obj.job.job_title
    
    def validate(self, data):
        """
        Validate job application data
        """
        # Check if the job is still active/open
        job = data.get('job')
        if job and job.job_status != 'open':
            raise serializers.ValidationError(
                "Cannot apply to a job that is not open."
            )
        
        # Check if application deadline has passed
        if job and job.application_deadline:
            if job.application_deadline < timezone.now():
                raise serializers.ValidationError(
                    "Application deadline has passed for this job."
                )
        
        # Validate expected rate is positive
        expected_rate = data.get('expected_rate')
        if expected_rate and expected_rate <= 0:
            raise serializers.ValidationError(
                "Expected rate must be greater than zero."
            )
        
        return data


class JobApplicationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing job applications
    """
    freelancer_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'freelancer_name', 'job_title', 'status', 
            'expected_rate', 'date_applied'
        ]
    
    def get_freelancer_name(self, obj):
        """Get freelancer's full name or username"""
        if obj.freelancer.first_name and obj.freelancer.last_name:
            return f"{obj.freelancer.first_name} {obj.freelancer.last_name}"
        return obj.freelancer.username
    
    def get_job_title(self, obj):
        """Get the job title"""
        return obj.job.job_title