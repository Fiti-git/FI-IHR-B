from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import ChoiceGroup
from .serializers import ChoiceGroupSerializer, ChoiceItemSerializer


class AllChoicesAPIView(APIView):
    """
    Return all choices grouped by slug
    /api/choices/
    """

    def get(self, request):
        groups = ChoiceGroup.objects.filter(is_active=True)
        data = {}

        for group in groups:
            items = group.items.filter(is_active=True).order_by('sort_order')
            data[group.slug] = ChoiceItemSerializer(items, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class ChoiceGroupItemsAPIView(APIView):
    """
    Return items for a single group
    /api/choices/<group_slug>/
    """

    def get(self, request, group_slug):
        try:
            group = ChoiceGroup.objects.get(slug=group_slug, is_active=True)
        except ChoiceGroup.DoesNotExist:
            return Response(
                {"error": "Choice group not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        items = group.items.filter(is_active=True).order_by('sort_order')
        serialized_items = ChoiceItemSerializer(items, many=True)

        return Response({
            "slug": group.slug,
            "name": group.name,
            "items": serialized_items.data
        }, status=status.HTTP_200_OK)
