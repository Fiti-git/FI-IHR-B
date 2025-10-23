from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FreelancerProfileViewSet, JobProviderProfileViewSet

router = DefaultRouter()
router.register(r'freelancer', FreelancerProfileViewSet, basename='freelancer-profile')
router.register(r'job-provider', JobProviderProfileViewSet, basename='jobprovider-profile')

urlpatterns = [
    path('', include(router.urls)),
]