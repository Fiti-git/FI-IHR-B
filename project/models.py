from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    project_type = models.CharField(max_length=50, default='fixed_price')  # no choices
    deadline = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=50, default='public')  # no choices
    status = models.CharField(max_length=50, default='open')  # no choices
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to='project_images/',
        null=True,
        blank=True,
        help_text='Project cover image'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Proposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    cover_letter = models.TextField()
    status = models.CharField(max_length=50, default='submitted')  # no choices
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['project', 'freelancer']

    def __str__(self):
        return f"Proposal by {self.freelancer.username} for {self.project.title}"


class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')  # no choices
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} - {self.project.title}"


class MilestonePayment(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='payments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_status = models.CharField(max_length=50, default='pending')  # no choices
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for {self.milestone.name} - {self.payment_status}"


class Feedback(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='feedbacks')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedbacks')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedbacks')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['project', 'client', 'freelancer']

    def __str__(self):
        return f"Feedback for {self.freelancer.username} - {self.rating} stars"


class ProjectTag(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=100)

    class Meta:
        unique_together = ['project', 'tag']

    def __str__(self):
        return f"{self.tag} - {self.project.title}"
