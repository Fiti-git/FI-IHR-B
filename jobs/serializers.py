from rest_framework import serializers
from django.utils import timezone
from .models import JobPosting, JobApplication, JobInterview, JobOffer, ApplicationWithdrawal


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for JobPosting model
    """
    
    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ['date_posted', 'job_status']


class JobPostingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating JobPosting model - excludes job_provider_id and work_mode
    """
    
    class Meta:
        model = JobPosting
        fields = [
            'job_title', 'department', 'job_type', 'work_location', 'role_overview',
            'key_responsibilities', 'required_qualifications', 'preferred_qualifications',
            'languages_required', 'job_category', 'salary_from', 'salary_to', 'currency',
            'application_deadline', 'application_method', 'interview_mode', 'hiring_manager',
            'number_of_openings', 'expected_start_date', 'screening_questions', 'file_upload',
            'health_insurance', 'remote_work', 'paid_leave', 'bonus'
        ]
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
        fields = ['id', 'job_id', 'freelancer_id', 'resume', 'cover_letter', 'expected_rate', 'status', 'date_applied', 'rating', 'comments']
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


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating job applications - simplified request
    """
    job_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_posting.id")
    
    class Meta:
        model = JobApplication
        fields = ['job_id', 'freelancer_id', 'resume', 'cover_letter']
    
    def create(self, validated_data):
        """
        Create a new job application
        """
        job_id = validated_data.pop('job_id')
        job = JobPosting.objects.get(id=job_id)
        validated_data['job'] = job
        return super().create(validated_data)
    
    def validate(self, data):
        """
        Validate job application data
        """
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


class JobApplicationJobListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing applications for a specific job with freelancer details
    """
    freelancer_name = serializers.CharField(default="Unknown", help_text="Freelancer name (placeholder)")
    resume_url = serializers.URLField(source='resume', help_text="URL to resume")
    cover_letter_url = serializers.URLField(source='cover_letter', help_text="URL to cover letter")
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'freelancer_name', 'resume_url', 'cover_letter_url', 
            'status', 'rating', 'comments'
        ]
    
    def to_representation(self, instance):
        """
        Customize the output representation
        """
        representation = super().to_representation(instance)
        representation['application_id'] = instance.id
        # Remove the 'id' field since we're using 'application_id'
        representation.pop('id', None)
        return representation


class JobApplicationReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviewing and rating job applications
    """
    
    class Meta:
        model = JobApplication
        fields = ['rating', 'status', 'comments']
    
    def validate_rating(self, value):
        """
        Validate rating is between 1 and 5
        """
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value
    
    def validate_status(self, value):
        """
        Validate status is one of the allowed choices
        """
        allowed_statuses = ['Pending', 'Accepted', 'Rejected', 'Save for Later']
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value


class JobApplicationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating job application status and rating
    """
    
    class Meta:
        model = JobApplication
        fields = ['status', 'rating', 'comments']
    
    def validate_rating(self, value):
        """
        Validate rating is between 1 and 5
        """
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value
    
    def validate_status(self, value):
        """
        Validate status is one of the allowed choices
        """
        allowed_statuses = ['Pending', 'Accepted', 'Rejected', 'Save for Later']
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value


class JobInterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for JobInterview model
    """
    application_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_application.id")
    
    class Meta:
        model = JobInterview
        fields = [
            'id', 'application_id', 'interview_date', 'interview_mode', 
            'status', 'interview_notes', 'interview_link', 'rating', 'comments'
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


class JobInterviewScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for scheduling interviews
    """
    application_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_application.id")
    date_time = serializers.DateTimeField(source='interview_date', help_text="Scheduled date and time")
    
    class Meta:
        model = JobInterview
        fields = [
            'application_id', 'date_time', 'interview_mode', 
            'interview_link', 'interview_notes'
        ]
    
    def create(self, validated_data):
        """
        Create a new scheduled interview
        """
        application_id = validated_data.pop('application_id')
        application = JobApplication.objects.get(id=application_id)
        validated_data['application'] = application
        return super().create(validated_data)
    
    def validate(self, data):
        """
        Validate interview scheduling data
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


class JobInterviewDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for interview details
    """
    date_time = serializers.DateTimeField(source='interview_date', help_text="Scheduled date and time")
    
    class Meta:
        model = JobInterview
        fields = [
            'id', 'application_id', 'date_time', 'interview_mode',
            'interview_link', 'interview_notes'
        ]
    
    def to_representation(self, instance):
        """
        Customize the output representation
        """
        representation = super().to_representation(instance)
        representation['interview_id'] = instance.id
        representation['application_id'] = instance.application.id
        # Remove the 'id' field since we're using 'interview_id'
        representation.pop('id', None)
        return representation


class JobInterviewFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for providing interview feedback
    """
    interview_id = serializers.IntegerField(write_only=True, help_text="Interview ID")
    
    class Meta:
        model = JobInterview
        fields = ['interview_id', 'rating', 'comments']
    
    def validate_rating(self, value):
        """
        Validate rating is between 1 and 5
        """
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value


class JobInterviewRescheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for rescheduling interviews
    """
    interview_id = serializers.IntegerField(write_only=True, help_text="Interview ID")
    new_date_time = serializers.DateTimeField(source='interview_date', help_text="New scheduled date and time")
    new_interview_link = serializers.URLField(source='interview_link', required=False, help_text="New interview link")
    
    class Meta:
        model = JobInterview
        fields = ['interview_id', 'new_date_time', 'new_interview_link']
    
    def validate_new_date_time(self, value):
        """
        Validate new interview date is not in the past
        """
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "New interview date cannot be in the past."
            )
        return value


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


class ApplicationWithdrawalSerializer(serializers.ModelSerializer):
    """
    Serializer for ApplicationWithdrawal model
    """
    application_id = serializers.IntegerField(write_only=True, help_text="Foreign key to job_application.id")
    
    class Meta:
        model = ApplicationWithdrawal
        fields = [
            'id', 'application_id', 'withdrawal_date', 'reason'
        ]
        read_only_fields = ['withdrawal_date']
    
    def create(self, validated_data):
        """
        Create a new application withdrawal
        """
        application_id = validated_data.pop('application_id')
        application = JobApplication.objects.get(id=application_id)
        validated_data['application'] = application
        
        # Update the application status to indicate withdrawal
        application.status = 'Withdrawn'
        application.save()
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """
        Customize the output representation to include application_id
        """
        representation = super().to_representation(instance)
        representation['application_id'] = instance.application.id
        return representation
    
    def validate(self, data):
        """
        Validate application withdrawal data
        """
        # Validate that the application exists
        application_id = data.get('application_id')
        if application_id:
            try:
                application = JobApplication.objects.get(id=application_id)
                # Check if application is already withdrawn
                if hasattr(application, 'withdrawal'):
                    raise serializers.ValidationError(
                        "This application has already been withdrawn."
                    )
                # Check if application is not in a withdrawable state
                if application.status in ['Accepted', 'Rejected']:
                    raise serializers.ValidationError(
                        f"Cannot withdraw application with status '{application.status}'."
                    )
            except JobApplication.DoesNotExist:
                raise serializers.ValidationError(
                    "Job application with this ID does not exist."
                )
        
        # Validate that reason is provided
        reason = data.get('reason')
        if not reason or not reason.strip():
            raise serializers.ValidationError(
                "Withdrawal reason is required and cannot be empty."
            )
        
        return data


class ApplicationWithdrawalListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing application withdrawals
    """
    application_id = serializers.IntegerField(source='application.id', read_only=True)
    
    class Meta:
        model = ApplicationWithdrawal
        fields = [
            'id', 'application_id', 'withdrawal_date'
        ]