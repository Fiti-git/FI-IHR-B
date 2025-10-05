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


class JobApplicationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating job application status - only update fields
    """
    rating = serializers.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        min_value=1, 
        max_value=5,
        required=False,
        help_text="Rating from 1 to 5"
    )
    status = serializers.ChoiceField(
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
            ('Save for Later', 'Save for Later'),
        ],
        required=False,
        help_text="Application status"
    )
    comments = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Update comments"
    )


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