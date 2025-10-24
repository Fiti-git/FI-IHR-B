from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, ProposalViewSet, MilestoneViewSet,
    MilestonePaymentViewSet, FeedbackViewSet, api_health_check
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'proposals', ProposalViewSet, basename='proposal')
router.register(r'milestones', MilestoneViewSet, basename='milestone')
router.register(r'payments', MilestonePaymentViewSet, basename='payment')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

urlpatterns = [
    # API Health Check endpoint
    path('health/', api_health_check, name='project-api-health-check'),
    
    # Router URLs - all CRUD operations for each model
    path('', include(router.urls)),
]