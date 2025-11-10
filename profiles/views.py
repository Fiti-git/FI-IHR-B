from rest_framework import viewsets, permissions, status
from .models import FreelancerProfile, JobProviderProfile
from .serializers import FreelancerProfileSerializer, JobProviderProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Import Django's built-in serializers
from rest_framework.serializers import Serializer, CharField


class FreelancerProfileView(APIView):
    """
    View to retrieve, create, or update the user's freelancer profile.
    REQUIRES AUTHENTICATION - for managing own profile
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, user):
        try:
            return FreelancerProfile.objects.get(user=user)
        except FreelancerProfile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        """ Retrieve the user's profile. """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {
                    'detail': 'Freelancer profile not found',
                    'user_type': 'not_freelancer',
                    'profile_exists': False
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, *args, **kwargs):
        """ Create a new profile for the user. """
        if FreelancerProfile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Profile already exists. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """ Update the user's existing profile. """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(
                profile, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(
                {"error": "Profile not found. Use POST to create one."},
                status=status.HTTP_404_NOT_FOUND
            )


class JobProviderProfileView(APIView):
    """
    View to retrieve, create, or update the user's job provider profile.
    REQUIRES AUTHENTICATION - for managing own profile
    """
    permission_classes = [IsAuthenticated]
    serializer_class = JobProviderProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, user):
        try:
            return JobProviderProfile.objects.get(user=user)
        except JobProviderProfile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        """
        Retrieve the authenticated user's profile.
        """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {
                    'detail': 'Job provider profile not found',
                    'user_type': 'not_job_provider',
                    'profile_exists': False
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, *args, **kwargs):
        """
        Create a new profile for the user.
        """
        if JobProviderProfile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Profile already exists. Use PUT method to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update the user's existing profile.
        """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(
                profile, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(
                {"error": "Profile not found. Use POST method to create one."},
                status=status.HTTP_404_NOT_FOUND
            )


# ============ PUBLIC LISTING VIEWS ============
class JobProviderListView(APIView):
    """
    PUBLIC view to retrieve all job provider profiles.
    NO AUTHENTICATION REQUIRED - for public listing page
    """
    permission_classes = [AllowAny]
    serializer_class = JobProviderProfileSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve all job provider profiles for public viewing.
        """
        profiles = JobProviderProfile.objects.all()
        serializer = self.serializer_class(profiles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FreelancerListView(APIView):
    """
    PUBLIC view to retrieve all freelancer profiles.
    NO AUTHENTICATION REQUIRED - for public listing page
    """
    permission_classes = [AllowAny]
    serializer_class = FreelancerProfileSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve all freelancer profiles for public viewing.
        """
        profiles = FreelancerProfile.objects.all()
        serializer = self.serializer_class(profiles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
# ============================================


class CheckAuthView(APIView):
    """
    PUBLIC endpoint to check if a user is authenticated.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'isAuthenticated': False,
                'username': None,
                'email': None,
                'roles': [],
                'is_freelancer': False,
                'is_job_provider': False
            })
        
        user = request.user
        roles = [group.name for group in user.groups.all()]
        is_freelancer = FreelancerProfile.objects.filter(user=user).exists()
        is_job_provider = JobProviderProfile.objects.filter(user=user).exists()

        return Response({
            'isAuthenticated': True,
            'username': user.username,
            'email': user.email,
            'roles': roles,
            'is_freelancer': is_freelancer,
            'is_job_provider': is_job_provider
        })


# Custom Serializer for changing password
class PasswordChangeSerializer(Serializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Old password is not correct")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value
        
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


# Custom Serializer for setting a new password (for social users)
class PasswordSetSerializer(Serializer):
    new_password = CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class PasswordStatusView(APIView):
    """
    Checks if the authenticated user has a usable password set.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({'has_password': user.has_usable_password()})


class ChangePasswordView(APIView):
    """
    Endpoint to change a password (if one exists) or set a password (for social auth users).
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user

        # If user has a password, they must provide the old one
        if user.has_usable_password():
            serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        # If user has no password (social auth), they can set a new one directly
        else:
            serializer = PasswordSetSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)