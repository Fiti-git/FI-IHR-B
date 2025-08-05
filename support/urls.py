from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupportTicketViewSet

router = DefaultRouter()
router.register(r'', SupportTicketViewSet, basename='support')

urlpatterns = [
  path('', include(router.urls)),
]
