from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FreelancerProfile, JobProviderProfile
from .serializers import FreelancerProfileSerializer, JobProviderProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework.permissions import IsAuthenticated

class FreelancerProfileView(APIView):
    """
    View to retrieve, create, or update the user's freelancer profile.
    """
    serializer_class = FreelancerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FreelancerProfileSerializer

    def get_queryset(self):
        """
        This view should return a list of all the profiles
        for the currently authenticated user.
        """
        return FreelancerProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Assign the current user to the profile when it is created.
        """
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override list to return the user's profile directly or 404 if not exists
        """
        try:
            profile = FreelancerProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except FreelancerProfile.DoesNotExist:
            return Response(
                {
                    'detail': 'Freelancer profile not found',
                    'user_type': 'freelancer',
                    'profile_exists': False
                },
                status=status.HTTP_404_NOT_FOUND
            )


class JobProviderProfileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing the profile of the currently authenticated user.
    """
    serializer_class = JobProviderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the profiles
        for the currently authenticated user.
        """
        return JobProviderProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Assign the current user to the profile when it is created.
        """
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override list to return the user's profile directly or 404 if not exists
        """
        try:
            profile = JobProviderProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except JobProviderProfile.DoesNotExist:
            return Response(
                {
                    'detail': 'Job provider profile not found',
                    'user_type': 'job-provider',
                    'profile_exists': False
                },
                status=status.HTTP_404_NOT_FOUND
            )
