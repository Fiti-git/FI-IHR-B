from django.urls import path
from .views import JobInterviewViewSet

app_name = 'job_interviews'

# Standard URL patterns for JobInterview
job_interview_list = JobInterviewViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

job_interview_detail = JobInterviewViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', job_interview_list, name='job-interview-list'),
    path('<int:pk>/', job_interview_detail, name='job-interview-detail'),
]