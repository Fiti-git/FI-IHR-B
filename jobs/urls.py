from django.urls import path
from .views import JobPostingViewSet

app_name = 'jobs'

# Create custom URL patterns to use job_id instead of id for JobPosting
job_posting_list = JobPostingViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

job_posting_detail = JobPostingViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    # Job Posting URLs
    path('', job_posting_list, name='job-posting-list'),
    path('<int:job_id>/', job_posting_detail, name='job-posting-detail'),
]