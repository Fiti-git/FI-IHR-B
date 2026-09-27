# myapi/urls.py

from django.urls import path
from .views import (
    RecentAdminActionsAPIView,
    SignUpView,
    SignInView,
    SetRoleView,
    get_csrf_token,
    AdminUserPermissionsAPIView,
    MyPermissionsAPIView,
    LoggedInUserView
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('set-role/', SetRoleView.as_view(), name='set-role'),
    path('csrf/', get_csrf_token, name='get-csrf-token'),
    path(
        "api/admin/users/permissions/",AdminUserPermissionsAPIView.as_view(),name="admin-user-permissions" ),
    path("admin/me/permissions/",MyPermissionsAPIView.as_view(),name="my-permissions",
    ),
    path('admin/recent-actions/', RecentAdminActionsAPIView.as_view(), name='recent-admin-actions'),
    path('admin/me/', LoggedInUserView.as_view(), name='logged-in-user'),

]
