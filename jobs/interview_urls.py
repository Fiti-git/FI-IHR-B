from django.urls import path
from .views import JobInterviewViewSet

app_name = 'job_interviews'

# Custom endpoints matching API specifications
interview_schedule = JobInterviewViewSet.as_view({
    'post': 'schedule_interview'
})

interview_detail = JobInterviewViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

interview_feedback = JobInterviewViewSet.as_view({
    'post': 'provide_feedback'
})

interview_reschedule = JobInterviewViewSet.as_view({
    'post': 'reschedule_interview'
})

urlpatterns = [
    # POST /api/job-interview/schedule
    path('schedule/', interview_schedule, name='interview-schedule'),
    # GET /api/job-interview/{interview_id}
    path('<int:interview_id>/', interview_detail, name='interview-detail'),
    # POST /api/job-interview/feedback
    path('feedback/', interview_feedback, name='interview-feedback'),
    # POST /api/job-interview/reschedule
    path('reschedule/', interview_reschedule, name='interview-reschedule'),
]