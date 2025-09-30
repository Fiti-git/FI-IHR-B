from django.urls import path
from .views import JobOfferViewSet

app_name = 'job_offers'

# Standard URL patterns for JobOffer
job_offer_list = JobOfferViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

job_offer_detail = JobOfferViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', job_offer_list, name='job-offer-list'),
    path('<int:pk>/', job_offer_detail, name='job-offer-detail'),
]