from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ['id', 'tag']


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            # Original fields
            'id', 'user', 'user_id', 'title', 'description', 'category', 
            'budget', 'project_type', 'deadline', 'visibility', 'status',
            'created_at', 'updated_at', 'tags', 'tag_list',
            # Additional testing fields - can be removed later
            'client_instructions', 'freelancer_location', 'project_duration',
            'freelancer_count', 'payment_terms'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user', 'tags']  # Added user and tags to read_only

    def create(self, validated_data):
        """Don't handle user here - let perform_create handle it"""
        # Remove user_id if present (perform_create will handle user)
        validated_data.pop('user_id', None)
        
        # Don't set user here - perform_create will handle it
        return Project(**validated_data)

    # Add validation for budget
    def validate_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero")
        return value
    
    # Add validation for deadline
    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past")
        return value
    
    def to_representation(self, instance):
        # Optimize by using select_related for user
        if isinstance(instance, Project):
            instance = Project.objects.select_related('user').get(id=instance.id)
        return super().to_representation(instance)


class ProposalSerializer(serializers.ModelSerializer):
    freelancer = UserSerializer(read_only=True)
    freelancer_id = serializers.IntegerField(write_only=True, required=False)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'project', 'project_title', 'freelancer', 'freelancer_id',
            'budget', 'cover_letter', 'status', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['submitted_at', 'updated_at']
    
    def create(self, validated_data):
        if 'freelancer_id' not in validated_data:
            validated_data['freelancer'] = self.context['request'].user
        else:
            freelancer_id = validated_data.pop('freelancer_id')
            validated_data['freelancer_id'] = freelancer_id
        return super().create(validated_data)

    # Add validation to check if project is still open
    def validate_project(self, value):
        if value.status != 'open':
            raise serializers.ValidationError("Cannot submit proposal for a closed project")
        return value


class MilestoneSerializer(serializers.ModelSerializer):
    freelancer = UserSerializer(read_only=True)
    freelancer_id = serializers.IntegerField(write_only=True, required=False)
    project_title = serializers.CharField(source='project.title', read_only=True)
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Milestone
        fields = [
            'id', 'project', 'project_title', 'freelancer', 'freelancer_id',
            'name', 'start_date', 'end_date', 'budget', 'status', 
            'description', 'created_at', 'updated_at', 'remaining_time'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_remaining_time(self, obj):
        if obj.end_date > timezone.now():
            return (obj.end_date - timezone.now()).days
        return 0


class MilestonePaymentSerializer(serializers.ModelSerializer):
    freelancer = UserSerializer(read_only=True)
    freelancer_id = serializers.IntegerField(write_only=True, required=False)
    milestone_name = serializers.CharField(source='milestone.name', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = MilestonePayment
        fields = [
            'id', 'milestone', 'milestone_name', 'project', 'project_title',
            'freelancer', 'freelancer_id', 'payment_status', 'payment_amount',
            'payment_date', 'payment_method', 'created_at', 'released_at'
        ]
        read_only_fields = ['created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    client_id = serializers.IntegerField(write_only=True, required=False)
    freelancer = UserSerializer(read_only=True)
    freelancer_id = serializers.IntegerField(write_only=True, required=False)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'project', 'project_title', 'client', 'client_id',
            'freelancer', 'freelancer_id', 'rating', 'feedback', 'submitted_at'
        ]
        read_only_fields = ['submitted_at']
    
    def create(self, validated_data):
        if 'client_id' not in validated_data:
            validated_data['client'] = self.context['request'].user
        else:
            client_id = validated_data.pop('client_id')
            validated_data['client_id'] = client_id
        return super().create(validated_data)