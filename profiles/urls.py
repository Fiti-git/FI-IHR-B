from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FreelancerProfileViewSet, JobProviderProfileViewSet

router = DefaultRouter()
router.register(r'freelancer/profile', FreelancerProfileViewSet, basename='freelancer-profile')
router.register(r'job-provider/profile', JobProviderProfileViewSet, basename='jobprovider-profile')

urlpatterns = [
    path('profile/api/', include(router.urls)),
]
