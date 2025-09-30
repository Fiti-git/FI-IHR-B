from rest_framework import serializers
from django.utils import timezone
from .models import JobPosting


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for JobPosting model
    """
    
    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ['date_posted', 'job_status']
    
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
        
        # Validate application deadline - convert to date for comparison if it's a string
        application_deadline = data.get('application_deadline')
        if application_deadline:
            # If it's a string, parse it
            if isinstance(application_deadline, str):
                try:
                    from datetime import datetime
                    deadline_date = datetime.strptime(application_deadline, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError(
                        "Application deadline must be in YYYY-MM-DD format."
                    )
            else:
                deadline_date = application_deadline.date() if hasattr(application_deadline, 'date') else application_deadline
            
            if deadline_date < timezone.now().date():
                raise serializers.ValidationError(
                    "Application deadline cannot be in the past."
                )
        
        # Validate expected start date
        expected_start_date = data.get('expected_start_date')
        if expected_start_date:
            # If it's a string, parse it
            if isinstance(expected_start_date, str):
                try:
                    from datetime import datetime
                    start_date = datetime.strptime(expected_start_date, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError(
                        "Expected start date must be in YYYY-MM-DD format."
                    )
            else:
                start_date = expected_start_date.date() if hasattr(expected_start_date, 'date') else expected_start_date
            
            if start_date < timezone.now().date():
                raise serializers.ValidationError(
                    "Expected start date cannot be in the past."
                )
        
        return data


class JobPostingListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing job postings
    """
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'job_title', 'department', 'job_type', 'work_location',
            'work_mode', 'job_category', 'application_deadline',
            'number_of_openings', 'job_status', 'date_posted'
        ]