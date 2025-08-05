from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    employer = serializers.HiddenField( default=serializers.CurrentUserDefault()  )
    docs     = serializers.FileField(use_url=True, required=False, allow_null=True)

    class Meta:
        model  = Project
        fields = [
            'id',
            'name',
            'employer', 
            'desc',
            'docs',
            'skillset',
            'payment_type',
            'price',
            'status',
            'freelancer',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
