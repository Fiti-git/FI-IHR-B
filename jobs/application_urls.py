from django.urls import path
from .views import JobApplicationViewSet

app_name = 'job_applications'

# Standard URL patterns for JobApplication
job_application_list = JobApplicationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

job_application_detail = JobApplicationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', job_application_list, name='job-application-list'),
    path('<int:pk>/', job_application_detail, name='job-application-detail'),
]