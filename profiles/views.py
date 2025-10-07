from rest_framework.viewsets import ModelViewSet
from .models import FreelancerProfile, JobProviderProfile
from .serializers import FreelancerProfileSerializer, JobProviderProfileSerializer

class FreelancerProfileViewSet(ModelViewSet):
    queryset = FreelancerProfile.objects.all()
    serializer_class = FreelancerProfileSerializer

class JobProviderProfileViewSet(ModelViewSet):
    queryset = JobProviderProfile.objects.all()
    serializer_class = JobProviderProfileSerializer
