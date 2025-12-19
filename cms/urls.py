from django.urls import path
from .views import (
    ServiceDetailAPIView,
    ServiceListAPIView,
    ServiceHeaderAPIView,
    ServiceContentAPIView,
    ContactMessageCreateAPIView,
    ServiceCategoryListAPIView,
    ServiceDetailAPIView,
)

urlpatterns = [
    path("services/", ServiceListAPIView.as_view()),
    path("services/<int:id>/header/", ServiceHeaderAPIView.as_view()),
    path("services/<int:id>/content/", ServiceContentAPIView.as_view()),
    path("contact/", ContactMessageCreateAPIView.as_view()),
    path("service-categories/", ServiceCategoryListAPIView.as_view()),
    path("services/<int:pk>/", ServiceDetailAPIView.as_view()),

]

