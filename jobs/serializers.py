from rest_framework import serializers
from django.utils import timezone
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Simplified JobPosting serializer - common fields only
    Excludes job_provider (handled automatically for authenticated users)
    """
    class Meta:
        model = JobPosting
        exclude = ['job_provider']
        read_only_fields = ['job_status']


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Simplified JobApplication serializer - common fields only
    Excludes expected_rate, status, rating, comments from POST requests
    """
    job_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = JobApplication
        fields = '__all__'


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
        fields = ['id', 'offer_status', 'offer_details', 'date_offered', 'date_accepted', 'date_rejected']
        read_only_fields = ['id', 'date_offered', 'date_accepted', 'date_rejected']


class JobOfferCreateSerializer(serializers.Serializer):
    """
    Serializer for creating job offers with structured offer details
    """
    application_id = serializers.IntegerField(help_text="ID of the job application")
    offer_details = serializers.JSONField(
        help_text="Structured offer details including salary, start_date, and benefits"
    )
    offer_status = serializers.ChoiceField(
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
            ('Withdrawn', 'Withdrawn'),
        ],
        default='Pending',
        help_text="Status of the offer"
    )
    
    def validate_offer_details(self, value):
        """
        Validate the offer_details structure
        """
        required_fields = ['salary', 'start_date', 'benefits']
        missing_fields = [field for field in required_fields if field not in value]
        
        if missing_fields:
            raise serializers.ValidationError(
                f"Missing required fields in offer_details: {', '.join(missing_fields)}"
            )
        
        # Validate salary is numeric
        try:
            salary = float(value['salary'])
            if salary <= 0:
                raise serializers.ValidationError("Salary must be a positive number")
        except (ValueError, TypeError):
            raise serializers.ValidationError("Salary must be a valid number")
        
        # Validate start_date format
        try:
            from datetime import datetime
            datetime.strptime(value['start_date'], '%Y-%m-%d')
        except ValueError:
            raise serializers.ValidationError("start_date must be in YYYY-MM-DD format")
        
        # Validate benefits is a list
        if not isinstance(value['benefits'], list):
            raise serializers.ValidationError("Benefits must be a list")
        
        return value


class ApplicationWithdrawalSerializer(serializers.ModelSerializer):
    """
    Simplified ApplicationWithdrawal serializer - common fields only
    """
    class Meta:
        model = ApplicationWithdrawal
        fields = '__all__'