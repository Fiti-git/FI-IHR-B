from django.urls import path
from .views import UserEngagementAPIView, CreateSupportTicketAPIView, AddTicketMessageAPIView, TicketListAPIView, TicketDetailAPIView, UpdateTicketStatusAPIView

urlpatterns = [
    path(
        'user-engagement/<int:user_id>/',
        UserEngagementAPIView.as_view(),
        name='user-engagement'
    ),
    path(
        'tickets/create/',
        CreateSupportTicketAPIView.as_view(),
        name='create-support-ticket'
    ),
    path(
        'tickets/<int:ticket_id>/message/',
        AddTicketMessageAPIView.as_view(),
        name='add-ticket-message'
    ),
    path(
        'tickets/user/<int:user_id>/',
        TicketListAPIView.as_view(),
        name='ticket-list'
    ),
    path(
        'tickets/<int:ticket_id>/',
        TicketDetailAPIView.as_view(),
        name='ticket-detail'
    ),
    path(
        'tickets/<int:ticket_id>/status/',
        UpdateTicketStatusAPIView.as_view(),
        name='update-ticket-status'
    ),
]
