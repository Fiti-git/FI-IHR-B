from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    list:     GET    /api/projects/
    create:   POST   /api/projects/
    retrieve: GET    /api/projects/{id}/
    update:   PUT    /api/projects/{id}/
    partial:  PATCH  /api/projects/{id}/
    destroy:  DELETE /api/projects/{id}/
    """
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employer', 'status', 'freelancer']

