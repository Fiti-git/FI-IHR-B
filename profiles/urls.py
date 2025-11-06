from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import the new APIView, not the old ViewSet
from .views import FreelancerProfileView, JobProviderProfileView, CheckAuthView,JobProviderListView,FreelancerListView

# The router is now empty or only contains other ViewSets
router = DefaultRouter()
# router.register(...) # Register other viewsets if you have them

urlpatterns = [
    path('', include(router.urls)),
    # Add the path for the job provider profile
    path('job-provider/', JobProviderProfileView.as_view(), name='job-provider-profile'),
    # Add the new path for the freelancer profile
    path('freelancer/', FreelancerProfileView.as_view(), name='freelancer-profile'),
    path('check-auth/', CheckAuthView.as_view(), name='check-auth'),
    
    # PUBLIC ENDPOINT (plural - for all profiles listing)
    path('job-providers/', JobProviderListView.as_view(), name='job-provider-list'),  # get data view employees
    path('freelancers/', FreelancerListView.as_view(), name='freelancer-list'),# get data view freelancers
]