# # jobs/urls.py
from django.urls import path
from .views import (
    JobPostingViewSet, 
    JobApplicationViewSet, 
    JobInterviewViewSet, 
    JobOfferViewSet, 
    ApplicationWithdrawalViewSet
)

app_name = 'jobs'

# ===== JOB POSTING URLS =====
job_posting_list = JobPostingViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

job_posting_detail = JobPostingViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

job_posting_manage = JobPostingViewSet.as_view({
    'get': 'job_manage'
})

# ===== JOB APPLICATION URLS =====
job_application_list = JobApplicationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

job_application_by_job = JobApplicationViewSet.as_view({
    'get': 'get_applications_for_job'
})

job_application_review = JobApplicationViewSet.as_view({
    'post': 'review_application'
})

job_application_update_status = JobApplicationViewSet.as_view({
    'put': 'update_application_status'
})

# ===== JOB INTERVIEW URLS =====
interview_schedule = JobInterviewViewSet.as_view({
    'post': 'schedule_interview'
})

interview_detail = JobInterviewViewSet.as_view({
    'get': 'retrieve'
})

interview_by_application = JobInterviewViewSet.as_view({
    'get': 'get_by_application'
})

interview_feedback = JobInterviewViewSet.as_view({
    'post': 'provide_feedback'
})

interview_reschedule = JobInterviewViewSet.as_view({
    'post': 'reschedule_interview'
})

# ===== JOB OFFER URLS =====
job_offer_create = JobOfferViewSet.as_view({
    'post': 'create_offer'
})

job_offer_accept = JobOfferViewSet.as_view({
    'post': 'accept_offer'
})

job_offer_reject = JobOfferViewSet.as_view({
    'post': 'reject_offer'
})

# ===== APPLICATION WITHDRAWAL URLS =====
withdrawal_list = ApplicationWithdrawalViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

withdrawal_detail = ApplicationWithdrawalViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    # ===== JOB POSTING ENDPOINTS =====
    path('posting/', job_posting_list, name='job-posting-list'),
    path('posting/<int:job_id>/', job_posting_detail, name='job-posting-detail'),
    path('manage/', job_posting_manage, name='job-manage'),

    # ===== JOB APPLICATION ENDPOINTS =====
    path('application/', job_application_list, name='job-application-list'),
    path('application/job/<int:job_id>/', job_application_by_job, name='job-application-by-job'),
    path('applications/review/<int:application_id>/', job_application_review, name='job-application-review'),
    path('application/update/<int:application_id>/', job_application_update_status, name='job-application-update'),
    
    # ===== JOB INTERVIEW ENDPOINTS =====
    path('interview/schedule/', interview_schedule, name='interview-schedule'),
    path('interview/<int:interview_id>/', interview_detail, name='interview-detail'),
    path('interview/application/<int:application_id>/', interview_by_application, name='interview-by-application'),
    path('interview/feedback/', interview_feedback, name='interview-feedback'),
    path('interview/reschedule/', interview_reschedule, name='interview-reschedule'),
    
    # ===== JOB OFFER ENDPOINTS =====
    path('offer/create/', job_offer_create, name='job-offer-create'),
    path('offer/accept/', job_offer_accept, name='job-offer-accept'),
    path('offer/reject/', job_offer_reject, name='job-offer-reject'),
    
    # ===== APPLICATION WITHDRAWAL ENDPOINTS =====
    path('withdrawals/', withdrawal_list, name='application-withdrawal-list'),
    path('withdrawals/<int:pk>/', withdrawal_detail, name='application-withdrawal-detail'),
]
