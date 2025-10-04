from rest_framework import serializers
from django.utils import timezone
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Simplified JobPosting serializer - common fields only
    """
    class Meta:
        model = JobPosting
        fields = '__all__'


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Simplified JobApplication serializer - common fields only
    Excludes expected_rate, status, rating, comments from POST requests
    """
    job_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = JobApplication
        fields = ['id', 'job_id', 'freelancer_id', 'resume', 'cover_letter', 'date_applied', 'status', 'rating', 'comments']
        read_only_fields = ['date_applied', 'status', 'rating', 'comments']


class JobInterviewSerializer(serializers.ModelSerializer):
    """
    Simplified JobInterview serializer - common fields only
    """
    application_id = serializers.IntegerField(write_only=True)
    date_time = serializers.DateTimeField(source='interview_date', write_only=True)
    
    class Meta:
        model = JobInterview
        fields = ['application_id', 'date_time', 'interview_mode', 'interview_link', 'interview_notes', 'id', 'interview_date', 'status', 'rating']
        read_only_fields = ['id', 'interview_date', 'status', 'rating']


class JobOfferSerializer(serializers.ModelSerializer):
    """
    Simplified JobOffer serializer - common fields only
    """
    class Meta:
        model = JobOffer
        fields = ['id', 'offer_status', 'date_offered', 'date_accepted', 'date_rejected']
        read_only_fields = ['id', 'date_offered', 'date_accepted', 'date_rejected']


class ApplicationWithdrawalSerializer(serializers.ModelSerializer):
    """
    Simplified ApplicationWithdrawal serializer - common fields only
    """
    class Meta:
        model = ApplicationWithdrawal
        fields = '__all__'