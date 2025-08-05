from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'employer', 'status', 'created_at')
    list_filter = ('status', 'payment_type')
    search_fields = ('name', 'desc', 'skillset')
