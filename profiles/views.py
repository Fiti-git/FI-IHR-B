from rest_framework import viewsets, permissions
from .models import FreelancerProfile, JobProviderProfile
from .serializers import FreelancerProfileSerializer, JobProviderProfileSerializer

class FreelancerProfileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing the profile of the currently authenticated user.
    """
    serializer_class = FreelancerProfileSerializer
    # 1. Add permissions to ensure the user is logged in.
    permission_classes = [permissions.IsAuthenticated]

    # 2. Override get_queryset to filter profiles by the current user.
    def get_queryset(self):
        """
        This view should return a list of all the profiles
        for the currently authenticated user.
        """
        return FreelancerProfile.objects.filter(user=self.request.user)

    # 3. Override perform_create to automatically set the user on creation.
    def perform_create(self, serializer):
        """
        Assign the current user to the profile when it is created.
        """
        serializer.save(user=self.request.user)


class JobProviderProfileViewSet(viewsets.ModelViewSet):
    serializer_class = JobProviderProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobProviderProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)