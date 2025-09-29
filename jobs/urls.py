from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostingViewSet, JobApplicationViewSet

router = DefaultRouter()
router.register(r'postings', JobPostingViewSet, basename='jobposting')
router.register(r'applications', JobApplicationViewSet, basename='jobapplication')

app_name = 'jobs'

urlpatterns = [
    path('api/', include(router.urls)),
]