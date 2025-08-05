from django.db import models
from django.contrib.auth import get_user_model
from project.models import Project

User = get_user_model()

class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    desc = models.TextField(verbose_name="Description")
    docs = models.FileField(upload_to='support_docs/', blank=True, null=True)
    STATUS_CHOICES = [
        ('open',        'Open'),
        ('in_progress', 'In Progress'),
        ('closed',      'Closed'),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_updated', verbose_name="Last Updated By", )
    
    def __str__(self):
        return f"Ticket #{self.id} ({self.get_status_display()})"
