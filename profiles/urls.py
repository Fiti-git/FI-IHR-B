from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import the new APIView, not the old ViewSet
from .views import FreelancerProfileView, JobProviderProfileView

# The router is now empty or only contains other ViewSets
router = DefaultRouter()
# router.register(...) # Register other viewsets if you have them

urlpatterns = [
    path('', include(router.urls)),
    # Add the path for the job provider profile
    path('job-provider/', JobProviderProfileView.as_view(), name='job-provider-profile'),
    # Add the new path for the freelancer profile
    path('freelancer/', FreelancerProfileView.as_view(), name='freelancer-profile'),
]