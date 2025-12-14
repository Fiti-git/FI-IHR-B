from django.urls import path
from .views import AllChoicesAPIView, ChoiceGroupItemsAPIView

urlpatterns = [
    path('choices/', AllChoicesAPIView.as_view(), name='all-choices'),
    path('choices/<slug:group_slug>/', ChoiceGroupItemsAPIView.as_view(), name='choice-group-items'),
]
