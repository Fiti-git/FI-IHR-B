from rest_framework import viewsets, permissions, status
from .models import FreelancerProfile, JobProviderProfile
from .serializers import FreelancerProfileSerializer, JobProviderProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404

class FreelancerProfileView(APIView):
    """
    View to retrieve, create, or update the user's freelancer profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FreelancerProfileSerializer

    def get_object(self, user):
        try:
            return FreelancerProfile.objects.get(user=user)
        except FreelancerProfile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        """ Retrieve the user's profile. """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            # A new user won't have a profile, return empty data
            return Response({}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """ Create a new profile for the user. """
        if FreelancerProfile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Profile already exists. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """ Update the user's existing profile. """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(profile, data=request.data, partial=True)
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
    * Requires token authentication.
    * A user can only access their own profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobProviderProfileSerializer

    def get_object(self, user):
        """
        Helper method to get the profile for the current user.
        Handles the case where the profile does not exist.
        """
        try:
            return JobProviderProfile.objects.get(user=user)
        except JobProviderProfile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        """
        Retrieve the user's profile.
        """
        try:
            profile = self.get_object(request.user)
            serializer = self.serializer_class(profile)
            # We return the single object directly, not in a list
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            # It's okay if the profile doesn't exist yet, just return nothing
            return Response({}, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        """
        Create a new profile for the user.
        This should only work if they don't already have one.
        """
        if JobProviderProfile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Profile already exists. Use PUT method to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Associate the profile with the currently logged-in user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, *args, **kwargs):
        """
        Update the user's existing profile.
        """
        try:
            profile = self.get_object(request.user)
            # The 'partial=True' argument allows for PATCH-like behavior,
            # meaning not all fields are required for an update.
            serializer = self.serializer_class(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(
                {"error": "Profile not found. Use POST method to create one."},
                status=status.HTTP_404_NOT_FOUND
            )