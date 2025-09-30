from django.urls import path
from .views import ApplicationWithdrawalViewSet

app_name = 'application_withdrawals'

# Standard URL patterns for ApplicationWithdrawal
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
    path('', withdrawal_list, name='application-withdrawal-list'),
    path('<int:pk>/', withdrawal_detail, name='application-withdrawal-detail'),
]