from django.db import models
from django.contrib.auth.models import User


class SupportTicket(models.Model):

    # -------------------------
    # BASIC USER INFO
    # -------------------------
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )

    # -------------------------
    # TICKET TYPE & REFERENCE
    # -------------------------
    TICKET_TYPE_CHOICES = [
        ('project', 'Project'),
        ('job', 'Job'),
    ]

    ticket_type = models.CharField(
        max_length=20,
        choices=TICKET_TYPE_CHOICES
    )

    reference_id = models.PositiveIntegerField()
    reference_title = models.CharField(max_length=255)

    # -------------------------
    # CATEGORY & CONTENT
    # -------------------------
    CATEGORY_CHOICES = [
        ('payment', 'Payment Issue'),
        ('project', 'Project Issue'),
        ('job', 'Job Issue'),
        ('service', 'Service Question'),
        ('other', 'Other'),
    ]

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    subject = models.CharField(max_length=255)
    description = models.TextField()

    # -------------------------
    # STATUS & PRIORITY
    # -------------------------
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # -------------------------
    # CHAT (JSON BASED)
    # -------------------------
    messages = models.JSONField(
        default=list,
        blank=True
    )

    # -------------------------
    # ADMIN / SUPPORT
    # -------------------------
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    # -------------------------
    # TIMESTAMPS
    # -------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------
    # META
    # -------------------------
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
