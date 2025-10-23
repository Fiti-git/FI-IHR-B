from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FreelancerProfile, JobProviderProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = 'ProfilesUserSerializer'  # 👈 add this line add by thanidu


class FreelancerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = FreelancerProfile
        fields = '__all__'


class JobProviderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = JobProviderProfile
        fields = '__all__'