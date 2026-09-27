from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminAllFreelancersView,
    AdminEmployerListView,
    AdminProjectCreateView,
    AdminUserCRUDAPIView, 
    PermissionsListAPIView,
    UserPermissionDetailAPIView, 
    SupportTicketAdminViewSet,
    SupportReplyView,
    UserConversationListView,
    ServiceCategoryViewSet, 
    ServiceViewSet,
    ServiceSubHeadingViewSet, 
    ContactMessageViewSet,
    manual_service_update, # Import the new manual view
    ChoiceGroupViewSet, 
    ChoiceItemViewSet,
    AdminUserListView,
    AdminProfileDetailView,
    AdminCreateUserView,
    AdminProjectListView,
    AdminProjectDetailView,
    AdminProposalListView,
    AdminPaymentListView,
    AdminDashboardStatsView,
    AdminProposalDetailView,
    AdminMilestoneListView,
    AdminMilestoneDetailView,
    AdminFeedbackListView,
    AdminJobPostingViewSet,
    JobPostingCRUDViewSet
)
from . import views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'tickets', SupportTicketAdminViewSet, basename='support-ticket')
router.register(r'categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'subheadings', ServiceSubHeadingViewSet, basename='service-subheading')
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-message')
router.register(r'choice-groups', ChoiceGroupViewSet, basename='choice-group')
router.register(r'choice-items', ChoiceItemViewSet, basename='choice-item')

app_name = 'cadmin'

urlpatterns = [
    # --- 1. THE BYPASS ROUTE (Put this first!) ---
    # This specific URL pattern avoids the 405 by explicitly naming the action
    path('services/create-manual/', views.manual_service_create, name='manual-service-create'),
    path('services/<int:pk>/manual/', manual_service_update, name='manual-service-patch'),

    # --- 2. ROUTER URLS ---
    path('', include(router.urls)), 
    
    # --- 3. CLASS BASED VIEWS ---
    path('users/', AdminUserCRUDAPIView.as_view(), name='list-create-users'),
    path('users/<int:user_id>/', AdminUserCRUDAPIView.as_view(), name='retrieve-update-delete-user'),
    path('permissions/', PermissionsListAPIView.as_view(), name='list-permissions'),
    path('permissions/<int:pk>/', UserPermissionDetailAPIView.as_view(), name='permission-detail'),
    path('tickets/<int:pk>/support-reply/', SupportReplyView.as_view(), name='support-reply'),
    path('conversations/', UserConversationListView.as_view(), name='user-conversations'),
    
    # --- 4. FUNCTION BASED VIEWS ---
    path('staff-users/', views.staff_users, name='staff_users'),

    # --- 5. Profiles ---
    path('admin/all-profiles/', AdminUserListView.as_view(), name='admin_all_profiles'),

    path('admin/profile/<str:role>/<int:id>/', AdminProfileDetailView.as_view(), name='admin_profile_detail'),

    path('admin/create-user/', AdminCreateUserView.as_view(), name='admin_create_user'),

    # --- 6. PROJECT & PAYMENT MANAGEMENT (NEW) ---
# --- Project Endpoints ---
    # Used for the main table list
    path('projects/', AdminProjectListView.as_view(), name='admin-project-list'),
    # Used for the [id]/page.tsx Detail Workspace (returns nested profiles/milestones)
    path('projects/<int:pk>/', AdminProjectDetailView.as_view(), name='admin-project-detail'),

    path('projects/create/', AdminProjectCreateView.as_view(), name='admin-project-list-create'),
    path('employers/', AdminEmployerListView.as_view(), name='admin-employer-list'),

    # --- Proposal Endpoints ---
    # Global list of bids
    path('proposals/', AdminProposalListView.as_view(), name='admin-proposal-list'),
    # View or Update a specific bid (Accept/Reject)
    path('proposals/<int:pk>/', AdminProposalDetailView.as_view(), name='admin-proposal-detail'),

    # --- Milestone Endpoints ---
    path('milestones/', AdminMilestoneListView.as_view(), name='admin-milestone-list'),
    # Used to update milestone status (Pending -> Completed)
    path('milestones/<int:pk>/', AdminMilestoneDetailView.as_view(), name='admin-milestone-detail'),

    # --- Payment & Feedback Endpoints ---
    path('payments/', AdminPaymentListView.as_view(), name='admin-payment-list'),
    path('feedback/', AdminFeedbackListView.as_view(), name='admin-feedback-list'),

    path('freelancers/', AdminAllFreelancersView.as_view(), name='admin-freelancer-list'),


    path('admin/dashboard-stats/', AdminDashboardStatsView.as_view(), name='admin_stats'),


    # --- 7. Job Postings ---
    path('admin/jobs/', AdminJobPostingViewSet.as_view({'get': 'list'}), name='admin-job-list'),
    path('admin/jobs/<int:pk>/', JobPostingCRUDViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-job-detail'),
    path('admin/jobs/<int:pk>/assign-candidate/', JobPostingCRUDViewSet.as_view({
        'post': 'assign_candidate'
    }), name='admin-job-assign-candidate'),
    path('admin/jobs/create/', views.AdminJobCreateViewSet.as_view({'post': 'create'}), name='admin-job-create'),
    
]