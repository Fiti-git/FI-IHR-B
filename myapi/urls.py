from django.urls import path
from .views import SignUpView, SignInView, GoogleLoginView ,google_oauth_callback,linkedin_oauth_callback

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('google-oauth-callback/',google_oauth_callback, name='google-oauth-callback'),  # must match exactly
    path('linkedin-oauth-callback/', linkedin_oauth_callback, name='linkedin_oauth_callback'),
]
