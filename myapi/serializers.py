# myapi/serializers.py
from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer
from dj_rest_auth.registration.serializers import SocialLoginSerializer, VerifyEmailSerializer
from django.conf import settings

class CustomVerifyEmailSerializer(VerifyEmailSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

# A custom serializer to return more user detail
class UserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ('pk', 'username', 'email', 'first_name', 'last_name')


# A custom serializer for the social login
class CustomSocialLoginSerializer(SocialLoginSerializer):
    """
    This serializer is used to process the social login.
    It is designed to be provider-agnostic.
    """
    # You can add or override fields here if necessary.
    # For a basic setup, the default implementation is often sufficient.
    pass