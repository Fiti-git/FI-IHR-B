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

# New custom endpoints
job_interview_schedule = JobInterviewViewSet.as_view({
    'post': 'schedule_interview'
})

job_interview_feedback = JobInterviewViewSet.as_view({
    'post': 'provide_feedback'
})

job_interview_reschedule = JobInterviewViewSet.as_view({
    'post': 'reschedule_interview'
})

urlpatterns = [
    path('', job_interview_list, name='job-interview-list'),
    path('<int:interview_id>/', job_interview_detail, name='job-interview-detail'),
    path('schedule/', job_interview_schedule, name='job-interview-schedule'),
    path('feedback/', job_interview_feedback, name='job-interview-feedback'),
    path('reschedule/', job_interview_reschedule, name='job-interview-reschedule'),
]