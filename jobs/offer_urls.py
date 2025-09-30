from django.urls import path
from .views import JobOfferViewSet

app_name = 'job_offers'

# Custom endpoints only - as specified
job_offer_create = JobOfferViewSet.as_view({
    'post': 'create_offer'
})

job_offer_accept = JobOfferViewSet.as_view({
    'post': 'accept_offer'
})

job_offer_reject = JobOfferViewSet.as_view({
    'post': 'reject_offer'
})

urlpatterns = [
    path('create/', job_offer_create, name='job-offer-create'),
    path('accept/', job_offer_accept, name='job-offer-accept'),
    path('reject/', job_offer_reject, name='job-offer-reject'),
]