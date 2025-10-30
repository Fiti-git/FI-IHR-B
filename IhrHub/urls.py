from django.contrib import admin
from django.urls import path, include, re_path  # <-- add re_path here
from rest_framework import permissions
from .views import custom_swagger_ui
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from . import views  # for get_user_roles
from jobs.views import get_jobs_for_freelancer

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
# from myapi.views import GoogleLogin, auth_success, login_page, EmailVerificationRedirectView

# Swagger/OpenAPI schema setup
schema_view = get_schema_view(
    openapi.Info(
        title="IhrHub API",
        default_version='v1',
        description="API documentation for IhrHub",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],  # optional
)

urlpatterns = [
    # path('', login_page, name='login_page'),
    path('admin/', admin.site.urls),

    # Authentication routes
    # path('api/auth/', include('dj_rest_auth.urls')),
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('accounts/', include('allauth.urls')),
    # path('api/auth/google/', GoogleLogin.as_view(), name='google_api_login'),
    # path('verify-email-redirect/', EmailVerificationRedirectView.as_view(), name='verify_email_redirect'),
    # path('auth/success/', auth_success, name='auth_success'),

    # JWT Auth endpoints
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Swagger JSON schema endpoint - must be before swagger UI to avoid 404
    re_path(r'^swagger\.json$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Swagger UI and ReDoc endpoints
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Your custom Swagger UI view
    path('custom-swagger/', custom_swagger_ui, name='custom-swagger-ui'),

    # App routes
    path('api/support/', include('support.urls')),
    path('api/project/', include('project.urls')),
    path('api/job-', include('jobs.urls')),  # Job posting and related endpoints
    # path('api/auth/', include('accounts.urls')),
    path('api/profile/', include('profiles.urls')),

    # Login and Registration routes
    path('myapi/', include('myapi.urls')),

    # Custom route for user roles
    path('api/user/<int:user_id>/roles/', views.get_user_roles, name='get_user_roles'),
    # GET /api/freelance/{freelance_id}/ - Jobs related to a freelancer
    path('api/freelance/<int:freelance_id>/', get_jobs_for_freelancer, name='freelance-jobs'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
