from django.urls import path
from . import views

urlpatterns = [
    # Project URLs
    path('projects/', views.project_list, name='project-list'),
    path('projects/<int:pk>/', views.project_detail, name='project-detail'),
    path('projects/<int:pk>/status/', views.project_update_status, name='project-status'),
    
    # Proposal URLs
    path('proposals/', views.proposal_list, name='proposal-list'),
    path('proposals/<int:pk>/', views.proposal_detail, name='proposal-detail'),
    path('proposals/<int:pk>/status/', views.proposal_update_status, name='proposal-status'),
    
    # Milestone URLs
    path('milestones/', views.milestone_list, name='milestone-list'),
    path('milestones/<int:pk>/', views.milestone_detail, name='milestone-detail'),
    path('milestones/<int:pk>/complete/', views.milestone_complete, name='milestone-complete'),
    
    # Payment URLs
    path('payments/', views.payment_list, name='payment-list'),
    path('payments/<int:pk>/release/', views.payment_release, name='payment-release'),
    
    # Feedback URLs
    path('feedback/', views.feedback_list, name='feedback-list'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback-detail'),
]