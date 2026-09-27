# cadmin/serializers.py
import json
from django.contrib.auth.models import User
from rest_framework import serializers
from support.models import SupportTicket
from jobs.models import JobPosting
from project.models import Project
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from chat.models import Conversation, Message
from cms.models import ServiceCategory, Service, ServiceSubHeading, ContactMessage


User = get_user_model()

# A simple serializer for displaying user information
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# A minimal serializer for the related JobPosting
class RelatedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = ['id', 'job_title', 'department', 'job_status']

# A minimal serializer for the related Project
class RelatedProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'category', 'status']

# The main serializer for the SupportTicket
class SupportTicketSerializer(serializers.ModelSerializer):
    # Use the SimpleUserSerializer for read-only representations
    user = SimpleUserSerializer(read_only=True)
    assigned_to_details = SimpleUserSerializer(source='assigned_to', read_only=True)

    # For writing, we only need the ID. We restrict the queryset to staff members.
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True),
        allow_null=True,
        required=False,
        write_only=True # Use this field only for updating/creating
    )

    # This is our dynamic field for the related Job or Project
    reference_object = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'user', 'ticket_type', 'reference_id', 'reference_title',
            'reference_object', # The enriched object
            'category', 'subject', 'description', 'status', 'priority',
            'messages',
            'assigned_to', # For writing the ID
            'assigned_to_details', # For reading the user object
            'created_at', 'updated_at'
        ]
        read_only_fields = ['messages', 'created_at', 'updated_at', 'user']

    def get_reference_object(self, obj):
        """
        Dynamically fetches and serializes the related Job or Project
        based on the ticket_type.
        """
        if obj.ticket_type == 'job':
            try:
                job = JobPosting.objects.get(id=obj.reference_id)
                return RelatedJobSerializer(job).data
            except JobPosting.DoesNotExist:
                return None
        elif obj.ticket_type == 'project':
            try:
                project = Project.objects.get(id=obj.reference_id)
                return RelatedProjectSerializer(project).data
            except Project.DoesNotExist:
                return None
        return None

# A simple serializer for validating the new message
class MessageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2000)


# serializers.py


class AddMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=True, max_length=1000)

    class Meta:
        model = SupportTicket
        fields = ['message']  # Only need the message from request

    def validate(self, attrs):
        request = self.context['request']
        # Ensure only support/staff users can use this endpoint
        if not request.user.is_staff:
            raise serializers.ValidationError("Only support staff can reply to tickets.")
        return attrs

    def update(self, instance, validated_data):
        message_text = validated_data['message']
        request = self.context['request']

        new_message = {
            "sender": "support",
            "message": message_text,
            "sender_id": request.user.id,
            "timestamp": timezone.now().isoformat()  # ISO format with timezone
        }

        # Append to the messages JSONField (list)
        instance.messages.append(new_message)

        # Optional: update status to "in_progress" if it was open
        if instance.status == 'open':
            instance.status = 'in_progress'

        instance.save(update_fields=['messages', 'status', 'updated_at'])
        return instance
    


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'is_read', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    # This will return the list of users with the fields you requested
    participants = ParticipantSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    conversation_id = serializers.IntegerField(source='id')

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'pair_key', 'participants', 'messages']

# CMS Serializers

class ServiceSubHeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSubHeading
        fields = ['id', 'service', 'title', 'content', 'order']

class ServiceSerializer(serializers.ModelSerializer):
    # read_only=True because we handle saving nested data manually in create/update
    sub_headings = ServiceSubHeadingSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'image', 'header_text', 'is_active', 'sub_headings', 'created_at']

    def handle_subheadings(self, instance, sub_headings_raw):
        if sub_headings_raw:
            try:
                # Convert the string from FormData back into a Python list
                if isinstance(sub_headings_raw, str):
                    sub_headings_data = json.loads(sub_headings_raw)
                else:
                    sub_headings_data = sub_headings_raw

                # Syncing: Delete existing and recreate (simplest approach)
                instance.sub_headings.all().delete()
                for item in sub_headings_data:
                    ServiceSubHeading.objects.create(
                        service=instance,
                        title=item.get('title', ''),
                        content=item.get('content', ''),
                        order=item.get('order', 0)
                    )
            except Exception as e:
                print(f"Error processing subheadings: {e}")

    def create(self, validated_data):
        request = self.context.get('request')
        sub_headings_raw = request.data.get('sub_headings')
        
        service = Service.objects.create(**validated_data)
        self.handle_subheadings(service, sub_headings_raw)
        return service

    def update(self, instance, validated_data):
        request = self.context.get('request')
        sub_headings_raw = request.data.get('sub_headings')

        # Update core fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update subheadings
        self.handle_subheadings(instance, sub_headings_raw)
        return instance

class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'is_active', 'services', 'created_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

#choice mangers serializers

from rest_framework import serializers
from choices_manager.models import ChoiceGroup, ChoiceItem

class ChoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceItem
        fields = ['id', 'group', 'value', 'label', 'sort_order', 'is_active', 'created_at']

class ChoiceGroupSerializer(serializers.ModelSerializer):
    # Add a count field so the frontend knows how many items are in the group
    items_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = ChoiceGroup
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'items_count', 'created_at']
        read_only_fields = ['slug']

# Profile Serializer
from rest_framework import serializers
from profiles.models import FreelancerProfile, JobProviderProfile
from rest_framework import serializers
from profiles.models import FreelancerProfile, JobProviderProfile

class FreelancerProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user.email')
    display_name = serializers.ReadOnlyField(source='full_name')
    role = serializers.ReadOnlyField(default="freelancer")

    class Meta:
        model = FreelancerProfile
        fields = '__all__'

class JobProviderProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    display_name = serializers.ReadOnlyField(source='company_name')
    role = serializers.ReadOnlyField(default="employer")

    class Meta:
        model = JobProviderProfile
        fields = '__all__'

    def get_email(self, obj):
        return obj.email_address or obj.user.email
    

#projects serializers.py

from rest_framework import serializers
from project.models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag
from rest_framework import serializers
from django.contrib.auth.models import User
from profiles.models import FreelancerProfile, JobProviderProfile

# --- PROFILE SERIALIZERS ---

class ProJobProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProviderProfile
        fields = '__all__'

class ProFreelancerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerProfile
        fields = '__all__'

# --- CHILD SERIALIZERS ---

class AdminMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'

class AdminProposalSerializer(serializers.ModelSerializer):
    # This navigates from the 'freelancer' field on the Proposal model 
    # to the 'freelancer_profile' related name on the User model.
    freelancer_details = ProFreelancerProfileSerializer(
        source='freelancer.freelancer_profile', 
        read_only=True
    )

    class Meta:
        model = Proposal
        fields = '__all__'

# --- PARENT PROJECT SERIALIZER ---

class AdminProjectSerializer(serializers.ModelSerializer):
    # Nesting the related models
    # Note: ensure 'related_name' in your Models match 'proposals' and 'milestones'
    proposals = AdminProposalSerializer(many=True, read_only=True)
    milestones = AdminMilestoneSerializer(many=True, read_only=True)
    
    # Navigates Project -> User -> JobProviderProfile
    employer_profile = ProJobProviderProfileSerializer(source='user.job_provider_profile', read_only=True)
    owner_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Project
        fields = [
            'id', 
            'title', 
            'description', 
            'category', 
            'budget', 
            'project_type', 
            'deadline', 
            'visibility', 
            'status', 
            'image',
            'created_at', 
            'updated_at', 
            'user',              # ID of the user who posted
            'owner_username',    # Username of the owner
            'employer_profile',  # Full profile details of the employer
            'proposals',         # List of all bids with freelancer profiles
            'milestones'         # List of all project milestones
        ]

# --- OTHER MANAGEMENT SERIALIZERS ---

class AdminPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestonePayment
        fields = '__all__'

class AdminFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class AdminProjectCreateSerializer(serializers.ModelSerializer):
    # This allows us to pass the User ID of the Job Provider
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Project
        fields = [
            'id', 'user', 'title', 'description', 'category', 
            'budget', 'project_type', 'deadline', 'visibility', 'status'
        ]

    def create(self, validated_data):
        # The project is created with the user ID selected in the frontend
        return Project.objects.create(**validated_data)
    

# Job Postings serializers.py

from rest_framework import serializers
from jobs.models import JobPosting
from profiles.models import JobProviderProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class JobProviderShortSerializer(serializers.ModelSerializer):
    """Serializer to provide basic company info for the job list"""
    class Meta:
        model = JobProviderProfile
        fields = ['id', 'company_name', 'profile_image', 'industry']

class AdminJobListingSerializer(serializers.ModelSerializer):
    # Nested provider details
    job_provider = JobProviderShortSerializer(read_only=True)
    
    # Get the username or full name of the assigned admin
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 
            'job_title', 
            'department', 
            'job_type', 
            'job_status', 
            'assigned_to_name', 
            'job_provider', 
            'number_of_openings', 
            'date_posted', 
            'application_deadline'
        ]

# job detalis serializer

from rest_framework import serializers
from jobs.models import JobPosting, JobApplication, JobInterview, JobOffer
from profiles.models import FreelancerProfile, JobProviderProfile

class FreelancerShortSerializer(serializers.ModelSerializer):
    """Basic profile info for listing applicants/interviewees"""
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = FreelancerProfile
        fields = ['id', 'username', 'full_name', 'professional_title', 'profile_image', 'city', 'country']

class JobDetailSerializer(serializers.ModelSerializer):
    job_provider = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    interviews = serializers.SerializerMethodField()
    selected_candidate = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = '__all__'

    def get_job_provider(self, obj):
        provider = obj.job_provider
        return {
            "company_name": provider.company_name,
            "industry": provider.industry,
            "image": provider.profile_image.url if provider.profile_image else None
        }

    def get_applicants(self, obj):
        # 1. Get all applications for this job
        applications = JobApplication.objects.filter(job=obj)
        data = []
        for app in applications:
            # 2. Get freelancer profile matching the freelancer_id (which is the User ID)
            profile = FreelancerProfile.objects.filter(user_id=app.freelancer_id).first()
            data.append({
                "application_id": app.id,
                "status": app.status,
                "date_applied": app.date_applied,
                "resume": app.resume.url if app.resume else None,
                "profile": FreelancerShortSerializer(profile).data if profile else None
            })
        return data

    def get_interviews(self, obj):
        # 3. Get all interviews for this job
        interviews = JobInterview.objects.filter(job=obj)
        data = []
        for interview in interviews:
            profile = FreelancerProfile.objects.filter(user_id=interview.freelancer_id).first()
            data.append({
                "interview_id": interview.id,
                "date": interview.interview_date,
                "mode": interview.interview_mode,
                "status": interview.status,
                "profile": FreelancerShortSerializer(profile).data if profile else None
            })
        return data

    def get_selected_candidate(self, obj):
        # 4. Check JobOffer table for Accepted status
        accepted_offer = JobOffer.objects.filter(
            application__job=obj, 
            offer_status='Accepted'
        ).first()
        
        if accepted_offer:
            user_id = accepted_offer.application.freelancer_id
            profile = FreelancerProfile.objects.filter(user_id=user_id).first()
            return FreelancerShortSerializer(profile).data
        return None
    

class JobCreateSerializer(serializers.ModelSerializer):
    # This allows you to send the ID of the employer in the POST request
    job_provider = serializers.PrimaryKeyRelatedField(queryset=JobProviderProfile.objects.all())

    class Meta:
        model = JobPosting
        fields = '__all__' # Or list every field from your JSON