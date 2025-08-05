# auth/urls.py
from django.urls import path
from .views import LoginView, RefreshView, LogoutView

urlpatterns = [
    path('login/',  LoginView.as_view(),    name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(),  name='token_refresh'),
    path('logout/', LogoutView.as_view(),    name='token_logout'),
]
