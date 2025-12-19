from rest_framework import generics, permissions
from .models import Service, ServiceCategory
from .serializers import (
    ServiceListSerializer,
    ServiceHeaderSerializer,
    ServiceContentSerializer,
    ContactMessageSerializer,
    ServiceCategorySerializer,

)


# API 1: id, name, category, image
class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True).select_related("category")
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]




# API 2: id, header_text
class ServiceHeaderAPIView(generics.RetrieveAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceHeaderSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


# API 3: id, multiple sub headings + content
class ServiceContentAPIView(generics.RetrieveAPIView):
    queryset = Service.objects.filter(is_active=True).prefetch_related("sub_headings")
    serializer_class = ServiceContentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


# API 4: Contact POST
class ContactMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

# API 5: List of Service Categories
class ServiceCategoryListAPIView(generics.ListAPIView):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer

# API 6: Service Detail by ID
class ServiceDetailAPIView(generics.RetrieveAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]