from rest_framework import serializers
from .models import ChoiceGroup, ChoiceItem


class ChoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceItem
        fields = ['id', 'label', 'value', 'sort_order', 'is_active']


class ChoiceGroupSerializer(serializers.ModelSerializer):
    items = ChoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = ChoiceGroup
        fields = ['id', 'name', 'slug', 'description', 'items']
