from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    name = models.CharField(max_length=255)
    employer = models.ForeignKey(User, related_name='employer_projects', on_delete=models.CASCADE)
    desc = models.TextField()
    docs = models.FileField(upload_to='project_docs/', blank=True, null=True)
    skillset = models.CharField(max_length=255, help_text="Comma-separated skills")
    category = models.CharField(max_length=100, blank=True)
    
    PAYMENT_TYPE_CHOICES = [
        (1, 'Fixed Price'),
        (2, 'Hourly'),
    ]
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    
    deadline = models.DateField(null=True, blank=True)
    
    freelancer = models.CharField(
        User,
        # related_name='assigned_projects',
        # on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Proposal(models.Model):
    project = models.ForeignKey(Project, related_name='proposals', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='proposals', on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    cover_letter = models.TextField()
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'freelancer']

    def __str__(self):
        return f"{self.freelancer.username} - {self.project.name}"


class Milestone(models.Model):
    project = models.ForeignKey(Project, related_name='milestones', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='milestones', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"


class MilestonePayment(models.Model):
    milestone = models.OneToOneField(Milestone, related_name='payment', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='payments', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('released', 'Released'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    PAYMENT_METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('stripe', 'Stripe'),
    ]
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.milestone.name}"


class Feedback(models.Model):
    project = models.ForeignKey(Project, related_name='feedbacks', on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='client_feedbacks', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='freelancer_feedbacks', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'client', 'freelancer']

    def __str__(self):
        return f"Feedback for {self.project.name} - {self.rating} stars"


class ProjectTag(models.Model):
    project = models.ForeignKey(Project, related_name='project_tags', on_delete=models.CASCADE)
    tag = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.project.name} - {self.tag}"