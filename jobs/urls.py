# from django.urls import path
# from .views import (
#     JobPostingViewSet, 
#     JobApplicationViewSet, 
#     JobInterviewViewSet, 
#     JobOfferViewSet, 
#     ApplicationWithdrawalViewSet
# )

# app_name = 'jobs'

# # ===== JOB POSTING URLS =====
# job_posting_list = JobPostingViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })

# job_posting_detail = JobPostingViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'delete': 'destroy'
# })

# # Job manage view (returns jobs/applications/interviews/offers for a provider)
# job_posting_manage = JobPostingViewSet.as_view({
#     'get': 'job_manage'
# })

# # ===== JOB APPLICATION URLS =====
# job_application_list = JobApplicationViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })

# job_application_by_job = JobApplicationViewSet.as_view({
#     'get': 'get_applications_for_job'
# })

# job_application_review = JobApplicationViewSet.as_view({
#     'post': 'review_application'
# })

# job_application_update_status = JobApplicationViewSet.as_view({
#     'put': 'update_application_status'
# })

# # ===== JOB INTERVIEW URLS =====
# interview_schedule = JobInterviewViewSet.as_view({
#     'post': 'schedule_interview'
# })

# interview_detail = JobInterviewViewSet.as_view({
#     'get': 'retrieve'
# })

# # GET /api/job-posting/interview/application/{application_id}/ - Get interview status and link by application
# interview_by_application = JobInterviewViewSet.as_view({
#     'get': 'get_by_application'
# })

# interview_feedback = JobInterviewViewSet.as_view({
#     'post': 'provide_feedback'
# })

# interview_reschedule = JobInterviewViewSet.as_view({
#     'post': 'reschedule_interview'
# })

# # ===== JOB OFFER URLS =====
# job_offer_create = JobOfferViewSet.as_view({
#     'post': 'create_offer'
# })

# job_offer_accept = JobOfferViewSet.as_view({
#     'post': 'accept_offer'
# })

# job_offer_reject = JobOfferViewSet.as_view({
#     'post': 'reject_offer'
# })

# # ===== APPLICATION WITHDRAWAL URLS =====
# withdrawal_list = ApplicationWithdrawalViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })

# withdrawal_detail = ApplicationWithdrawalViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })

# urlpatterns = [
#     # ===== JOB POSTING ENDPOINTS =====
#     # POST /api/job-posting/ - Create job posting
#     # GET /api/job-posting/ - List job postings
#     path('posting/', job_posting_list, name='job-posting-list'),
#     # GET /api/job-posting/{job_id}/ - Get specific job posting
#     # PUT /api/job-posting/{job_id}/ - Update job posting
#     # DELETE /api/job-posting/{job_id}/ - Delete job posting
#     path('posting/<int:job_id>/', job_posting_detail, name='job-posting-detail'),

#     # ===== JOB MANAGE ENDPOINTS =====
#     # GET /api/job-posting/manage/ - Get jobs and related data for a job provider
#     path('manage/', job_posting_manage, name='job-manage'),

#     # ===== JOB APPLICATION ENDPOINTS =====
#     # POST /api/job-posting/applications/ - Apply to job
#     # GET /api/job-posting/applications/ - List applications
#     path('application/', job_application_list, name='job-application-list'),
#     # GET /api/job-posting/applications/job/{job_id}/ - Get applications for specific job
#     path('application/job/<int:job_id>/', job_application_by_job, name='job-application-by-job'),
#     # POST /api/job-posting/applications/review/{application_id}/ - Review application
#     path('applications/review/<int:application_id>/', job_application_review, name='job-application-review'),
#     # PUT /api/job-posting/applications/update/{application_id}/ - Update application status
#     path('application/update/<int:application_id>/', job_application_update_status, name='job-application-update'),
    
#     # ===== JOB INTERVIEW ENDPOINTS =====
#     # POST /api/job-posting/interviews/schedule/ - Schedule interview
#     path('interview/schedule/', interview_schedule, name='interview-schedule'),
#     # GET /api/job-posting/interviews/{interview_id}/ - Get interview details
#     # GET /api/job-posting/interview/application/{application_id}/ - Get latest interview status and link for an application
#     # PUT /api/job-posting/interviews/{interview_id}/ - Update interview
#     path('interview/<int:interview_id>/', interview_detail, name='interview-detail'),
#     # GET /api/job-posting/interview/application/{application_id}/ - Get interview status/link by application
#     path('interview/application/<int:application_id>/', interview_by_application, name='interview-by-application'),
#     # POST /api/job-posting/interviews/feedback/ - Provide interview feedback
#     path('interview/feedback/', interview_feedback, name='interview-feedback'),
#     # POST /api/job-posting/interviews/reschedule/ - Reschedule interview
#     path('interview/reschedule/', interview_reschedule, name='interview-reschedule'),
    
#     # ===== JOB OFFER ENDPOINTS =====
#     # POST /api/job-posting/offers/create/ - Create job offer
#     path('offer/create/', job_offer_create, name='job-offer-create'),
#     # POST /api/job-posting/offers/accept/ - Accept job offer
#     path('offer/accept/', job_offer_accept, name='job-offer-accept'),
#     # POST /api/job-posting/offers/reject/ - Reject job offer
#     path('offer/reject/', job_offer_reject, name='job-offer-reject'),
    
#     # ===== APPLICATION WITHDRAWAL ENDPOINTS =====
#     # POST /api/job-posting/withdrawals/ - Withdraw application
#     # GET /api/job-posting/withdrawals/ - List withdrawals
#     path('withdrawals/', withdrawal_list, name='application-withdrawal-list'),
#     # GET /api/job-posting/withdrawals/{id}/ - Get specific withdrawal
#     path('withdrawals/<int:pk>/', withdrawal_detail, name='application-withdrawal-detail'),
# ]

# jobs/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    JobPostingViewSet,
    JobApplicationViewSet,
    JobInterviewViewSet,
    JobOfferViewSet,
    ApplicationWithdrawalViewSet
)

app_name = 'jobs'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'job-posting', JobPostingViewSet, basename='job-posting')
router.register(r'job-application', JobApplicationViewSet, basename='job-application')
router.register(r'job-interview', JobInterviewViewSet, basename='job-interview')
router.register(r'job-offer', JobOfferViewSet, basename='job-offer')
router.register(r'application-withdrawal', ApplicationWithdrawalViewSet, basename='application-withdrawal')

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]
