from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = 'ProjectUserSerializer'  # 👈 add this line add by thanidu

class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ['id', 'tag']


class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'user', 'title', 'description', 'category', 
            'budget', 'project_type', 'deadline', 'visibility', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def create(self, validated_data):
        """Create project instance - user will be set by perform_create in view"""
        return Project.objects.create(**validated_data)

    def validate_budget(self, value):
        """Validate budget is greater than zero"""
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero")
        return value
    
    def validate_deadline(self, value):
        """Validate deadline is in the future"""
        if value < timezone.now():
            raise serializers.ValidationError("Deadline must be in the future")
        return value
    
    def validate_project_type(self, value):
        """Validate project_type field"""
        valid_types = ['fixed_price', 'hourly']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid project type. Must be one of: {', '.join(valid_types)}"
            )
        return value
    
    def validate_visibility(self, value):
        """Validate visibility field"""
        valid_visibility = ['public', 'private']
        if value not in valid_visibility:
            raise serializers.ValidationError(
                f"Invalid visibility. Must be one of: {', '.join(valid_visibility)}"
            )
        return value
    
    def validate_status(self, value):
        valid_statuses = ['open', 'in_progress', 'completed', 'closed']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value


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

    def validate_project(self, value):
        """Validate project is still open"""
        if value.status != 'open':
            raise serializers.ValidationError("Cannot submit proposal for a closed project")
        return value
    
    def validate_budget(self, value):
        """Validate budget is greater than zero"""
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero")
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
    
    def validate(self, data):
        """Validate milestone dates"""
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )
        return data
    
    def validate_budget(self, value):
        """Validate budget is greater than zero"""
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero")
        return value


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
        read_only_fields = ['created_at', 'released_at']
    
    def validate_payment_amount(self, value):
        """Validate payment amount is greater than zero"""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero")
        return value


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
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value