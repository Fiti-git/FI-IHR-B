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

# Custom endpoints matching API specifications
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
    # POST /api/job-application
    path('', job_application_list, name='job-application-list'),
    # GET /api/job-application/{id}
    path('<int:pk>/', job_application_detail, name='job-application-detail'),
    # GET /api/job-application/job/{job_id}
    path('job/<int:job_id>/', job_application_by_job, name='job-application-by-job'),
    # POST /api/job-application/review/{application_id}
    path('review/<int:pk>/', job_application_review, name='job-application-review'),
    # PUT /api/job-application/update/{application_id}
    path('update/<int:pk>/', job_application_update_status, name='job-application-update'),
]