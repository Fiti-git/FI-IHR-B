from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    name = models.CharField(max_length=255)
    employer = models.ForeignKey(User, related_name='employer_projects', on_delete=models.CASCADE)
    desc = models.TextField()
    docs = models.FileField(upload_to='project_docs/', blank=True, null=True)
    skillset = models.CharField(max_length=255, help_text="Comma-separated skills")
    PAYMENT_TYPE_CHOICES = [
        (1, 'Fixed Price'),
        (2, 'Hourly'),
    ]
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('started', 'Posting Started'),
        ('ongoing', 'Ongoing'),
        ('ended',   'Ended'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='started')
    freelancer = models.ForeignKey(
        User,
        related_name='assigned_projects',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
