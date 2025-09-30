from rest_framework import serializers
from django.utils import timezone
from .models import JobPosting, JobApplication, JobInterview, JobOffer


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


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for JobApplication model
    """
    job_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_posting.id")
    
    class Meta:
        model = JobApplication
        fields = ['id', 'job_id', 'freelancer_id', 'resume', 'cover_letter', 'expected_rate', 'status', 'date_applied']
        read_only_fields = ['date_applied']
    
    def create(self, validated_data):
        """
        Create a new job application
        """
        job_id = validated_data.pop('job_id')
        job = JobPosting.objects.get(id=job_id)
        validated_data['job'] = job
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update a job application
        """
        if 'job_id' in validated_data:
            job_id = validated_data.pop('job_id')
            job = JobPosting.objects.get(id=job_id)
            validated_data['job'] = job
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        Customize the output representation to include job_id
        """
        representation = super().to_representation(instance)
        representation['job_id'] = instance.job.id
        return representation
    
    def validate(self, data):
        """
        Validate job application data
        """
        # Validate that expected_rate is positive
        expected_rate = data.get('expected_rate')
        if expected_rate and expected_rate <= 0:
            raise serializers.ValidationError(
                "Expected rate must be greater than 0."
            )
        
        # Validate that resume URL is provided
        resume = data.get('resume')
        if not resume:
            raise serializers.ValidationError(
                "Resume URL is required."
            )
        
        # Validate that the job exists
        job_id = data.get('job_id')
        if job_id and not JobPosting.objects.filter(id=job_id).exists():
            raise serializers.ValidationError(
                "Job posting with this ID does not exist."
            )
        
        return data


class JobApplicationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing job applications
    """
    job_id = serializers.IntegerField(source='job.id', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job_id', 'freelancer_id', 'status', 
            'expected_rate', 'date_applied'
        ]


class JobInterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for JobInterview model
    """
    application_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_application.id")
    
    class Meta:
        model = JobInterview
        fields = [
            'id', 'application_id', 'interview_date', 'interview_mode', 
            'status', 'interview_notes'
        ]
    
    def create(self, validated_data):
        """
        Create a new job interview
        """
        application_id = validated_data.pop('application_id')
        application = JobApplication.objects.get(id=application_id)
        validated_data['application'] = application
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update a job interview
        """
        if 'application_id' in validated_data:
            application_id = validated_data.pop('application_id')
            application = JobApplication.objects.get(id=application_id)
            validated_data['application'] = application
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        Customize the output representation to include application_id
        """
        representation = super().to_representation(instance)
        representation['application_id'] = instance.application.id
        return representation
    
    def validate(self, data):
        """
        Validate job interview data
        """
        # Validate that interview_date is not in the past
        interview_date = data.get('interview_date')
        if interview_date and interview_date < timezone.now():
            raise serializers.ValidationError(
                "Interview date cannot be in the past."
            )
        
        # Validate that the application exists
        application_id = data.get('application_id')
        if application_id and not JobApplication.objects.filter(id=application_id).exists():
            raise serializers.ValidationError(
                "Job application with this ID does not exist."
            )
        
        return data


class JobInterviewListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing job interviews
    """
    application_id = serializers.IntegerField(source='application.id', read_only=True)
    
    class Meta:
        model = JobInterview
        fields = [
            'id', 'application_id', 'interview_date', 'interview_mode', 'status'
        ]


class JobOfferSerializer(serializers.ModelSerializer):
    """
    Serializer for JobOffer model
    """
    application_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_application.id")
    
    class Meta:
        model = JobOffer
        fields = [
            'id', 'application_id', 'offer_status', 'offer_details',
            'date_offered', 'date_accepted', 'date_rejected'
        ]
        read_only_fields = ['date_offered']
    
    def create(self, validated_data):
        """
        Create a new job offer
        """
        application_id = validated_data.pop('application_id')
        application = JobApplication.objects.get(id=application_id)
        validated_data['application'] = application
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update a job offer
        """
        if 'application_id' in validated_data:
            application_id = validated_data.pop('application_id')
            application = JobApplication.objects.get(id=application_id)
            validated_data['application'] = application
        
        # Auto-set date_accepted or date_rejected based on status change
        new_status = validated_data.get('offer_status')
        if new_status and new_status != instance.offer_status:
            if new_status == 'Accepted' and not instance.date_accepted:
                validated_data['date_accepted'] = timezone.now()
                validated_data['date_rejected'] = None
            elif new_status == 'Rejected' and not instance.date_rejected:
                validated_data['date_rejected'] = timezone.now()
                validated_data['date_accepted'] = None
            elif new_status == 'Pending':
                validated_data['date_accepted'] = None
                validated_data['date_rejected'] = None
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        Customize the output representation to include application_id
        """
        representation = super().to_representation(instance)
        representation['application_id'] = instance.application.id
        return representation
    
    def validate(self, data):
        """
        Validate job offer data
        """
        # Validate that the application exists
        application_id = data.get('application_id')
        if application_id and not JobApplication.objects.filter(id=application_id).exists():
            raise serializers.ValidationError(
                "Job application with this ID does not exist."
            )
        
        # Validate that offer_details is provided
        offer_details = data.get('offer_details')
        if not offer_details or not offer_details.strip():
            raise serializers.ValidationError(
                "Offer details are required and cannot be empty."
            )
        
        return data


class JobOfferListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing job offers
    """
    application_id = serializers.IntegerField(source='application.id', read_only=True)
    
    class Meta:
        model = JobOffer
        fields = [
            'id', 'application_id', 'offer_status', 'date_offered'
        ]