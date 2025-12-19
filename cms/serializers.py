from rest_framework import serializers
from .models import Service, ServiceSubHeading, ContactMessage, ServiceCategory


class ServiceListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")

    class Meta:
        model = Service
        fields = ("id", "name", "category", "image")


class ServiceHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "header_text")


class ServiceSubHeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSubHeading
        fields = ("id", "title", "content", "order")


class ServiceContentSerializer(serializers.ModelSerializer):
    sub_headings = ServiceSubHeadingSerializer(many=True)

    class Meta:
        model = Service
        fields = ("id", "sub_headings")


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "message")

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name")
