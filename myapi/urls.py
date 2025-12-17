# myapi/urls.py

from django.urls import path
from .views import (
    SignUpView,
    SignInView,
    SetRoleView,
    get_csrf_token,
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('set-role/', SetRoleView.as_view(), name='set-role'),
    path('csrf/', get_csrf_token, name='get-csrf-token'),
]
