from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FreelancerProfile, JobProviderProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = 'ProfilesUserSerializer'


class FreelancerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    skills_list = serializers.SerializerMethodField()

    class Meta:
        model = FreelancerProfile
        fields = '__all__'

    def get_profile_image_url(self, obj):
        """Return full URL for profile image"""
        if obj.profile_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None

    def get_resume_url(self, obj):
        """Return full URL for resume"""
        if obj.resume:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.resume.url)
            return obj.resume.url
        return None

    def get_skills_list(self, obj):
        """Convert comma-separated skills to list"""
        if obj.skills:
            return [skill.strip() for skill in obj.skills.split(',')]
        return []


class JobProviderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = JobProviderProfile
        fields = '__all__'

    def get_profile_image_url(self, obj):
        """Return full URL for profile image"""
        if obj.profile_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None