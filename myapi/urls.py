# myapi/urls.py

from django.urls import path
from .views import (
    SignUpView,
    SignInView,
    GoogleLoginView,
    LinkedInLoginView,
    VerifyEmailView,
    SetRoleView,
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('linkedin-login/', LinkedInLoginView.as_view(), name='linkedin-login'), 
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('set-role/', SetRoleView.as_view(), name='set-role'),
]
