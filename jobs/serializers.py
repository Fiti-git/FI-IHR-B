from rest_framework import serializers
from .models import (
    JobPosting,
    JobApplication,
    JobInterview,
    JobOffer,
    ApplicationWithdrawal
)


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Simplified JobPosting serializer - common fields only
    Excludes job_provider (handled automatically for authenticated users)
    """
    class Meta:
        model = JobPosting
        exclude = ['job_provider']
        read_only_fields = []


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Simplified JobApplication serializer - common fields only
    Excludes expected_rate, status, rating, comments from POST requests
    """
    job_id = serializers.IntegerField(write_only=True)
    resume = serializers.FileField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = JobApplication
        exclude = ['expected_rate', 'status', 'rating', 'comments']


class JobApplicationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating job application status - only update fields
    NO hardcoded choices, NO backend validation conflicts
    """
    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        min_value=1,
        max_value=5,
        required=False,
        help_text="Rating from 1 to 5"
    )

    status = serializers.CharField(
        max_length=50,
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
    job_id = serializers.IntegerField(write_only=True)
    freelance_id = serializers.IntegerField(write_only=True)
    date_time = serializers.DateTimeField(source='interview_date', write_only=True)

    class Meta:
        model = JobInterview
        fields = [
            'application_id',
            'job_id',
            'freelance_id',
            'date_time',
            'interview_mode',
            'interview_link',
            'interview_notes',
            'id',
            'interview_date',
            'status',
            'rating',
        ]
        read_only_fields = ['id', 'interview_date', 'status', 'rating']


class JobOfferSerializer(serializers.ModelSerializer):
    """
    Simplified JobOffer serializer - common fields only
    """
    class Meta:
        model = JobOffer
        fields = [
            'id',
            'application',
            'offer_status',
            'offer_details',
            'date_offered',
            'date_accepted',
            'date_rejected',
            'multi_doc',
        ]
        read_only_fields = [
            'id',
            'date_offered',
            'date_accepted',
            'date_rejected',
        ]


class JobOfferCreateSerializer(serializers.Serializer):
    """
    Serializer for creating job offers
    NO hardcoded choices
    """
    application_id = serializers.IntegerField(
        help_text="ID of the job application"
    )

    offer_details = serializers.JSONField(
        help_text="Structured offer details including salary, start_date, and benefits"
    )

    offer_status = serializers.CharField(
        required=False,
        default='Pending',
        max_length=20,
        help_text="Status of the offer"
    )

    multi_doc = serializers.FileField(
        required=False,
        allow_null=True,
        help_text="Optional document file for the job offer"
    )

    def validate_offer_details(self, value):
        required_fields = ['salary', 'start_date', 'benefits']
        missing_fields = [f for f in required_fields if f not in value]

        if missing_fields:
            raise serializers.ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            salary = float(value['salary'])
            if salary <= 0:
                raise serializers.ValidationError("Salary must be positive")
        except (ValueError, TypeError):
            raise serializers.ValidationError("Salary must be a valid number")

        from datetime import datetime
        try:
            datetime.strptime(value['start_date'], '%Y-%m-%d')
        except ValueError:
            raise serializers.ValidationError("start_date must be YYYY-MM-DD")

        if not isinstance(value['benefits'], list):
            raise serializers.ValidationError("Benefits must be a list")

        return value


class JobOfferUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating job offers
    NO hardcoded choices
    """
    offer_status = serializers.CharField(
        required=False,
        max_length=20,
        help_text="Status of the offer"
    )

    offer_details = serializers.CharField(
        required=False,
        min_length=1,
        help_text="Detailed offer (salary, benefits, etc.)"
    )

    multi_doc = serializers.FileField(
        required=False,
        allow_null=True,
        help_text="Optional document file for the job offer"
    )


class ApplicationWithdrawalSerializer(serializers.ModelSerializer):
    """
    Simplified ApplicationWithdrawal serializer - common fields only
    """
    class Meta:
        model = ApplicationWithdrawal
        fields = '__all__'
