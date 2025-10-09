from rest_framework import serializers
from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag


class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ['id', 'tag']


class ProjectSerializer(serializers.ModelSerializer):
    employer = serializers.IntegerField()  # Changed from HiddenField
    employer_name = serializers.CharField(source='user.Id', read_only=True)
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), 
        write_only=True, 
        required=False
    )
    project_tags = ProjectTagSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'employer', 'employer_name', 'desc', 'docs', 
            'skillset', 'category', 'payment_type', 'price', 'status', 
            'visibility', 'deadline', 'freelancer', 'freelancer_name',
            'tags', 'project_tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        project = Project.objects.create(**validated_data)
        
        # Create tags
        for tag in tags:
            ProjectTag.objects.create(project=project, tag=tag)
        
        return project


class ProposalSerializer(serializers.ModelSerializer):
    freelancer = serializers.IntegerField()  # Changed from HiddenField
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)
    project_title = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Proposal
        fields = [
            'id', 'project', 'freelancer', 'freelancer_name', 
            'project_title', 'budget', 'cover_letter', 'status',
            'submitted_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'updated_at', 'status']


class MilestoneSerializer(serializers.ModelSerializer):
    freelancer = serializers.IntegerField()  # Changed from HiddenField
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Milestone
        fields = [
            'id', 'project', 'project_name', 'freelancer', 'freelancer_name',
            'name', 'description', 'start_date', 'end_date', 'budget', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MilestonePaymentSerializer(serializers.ModelSerializer):
    milestone_name = serializers.CharField(source='milestone.name', read_only=True)
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)

    class Meta:
        model = MilestonePayment
        fields = [
            'id', 'milestone', 'milestone_name', 'project', 'freelancer', 
            'freelancer_name', 'payment_amount', 'payment_status', 
            'payment_method', 'payment_date', 'released_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'payment_date', 'released_at']


class FeedbackSerializer(serializers.ModelSerializer):
    client = serializers.IntegerField()  # Changed from HiddenField
    client_name = serializers.CharField(source='client.username', read_only=True)
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'project', 'project_name', 'client', 'client_name',
            'freelancer', 'freelancer_name', 'rating', 'feedback', 
            'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']
