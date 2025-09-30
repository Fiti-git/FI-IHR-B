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

# New custom endpoints
job_application_by_job = JobApplicationViewSet.as_view({
    'get': 'get_applications_for_job'
})

job_application_review = JobApplicationViewSet.as_view({
    'post': 'review_application'
})

job_application_update_status = JobApplicationViewSet.as_view({
    'put': 'update_application_status'
})

urlpatterns = [
    path('', job_application_list, name='job-application-list'),
    path('<int:job_id>/', job_application_detail, name='job-application-detail'),
    path('job/<int:job_id>/', job_application_by_job, name='job-application-by-job'),
    path('review/<int:application_id>/', job_application_review, name='job-application-review'),
    path('update/<int:application_id>/', job_application_update_status, name='job-application-update'),
]