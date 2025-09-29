from django.db import models
from django.contrib.auth.models import User


class JobApplication(models.Model):
    """
    Job application model based on the requirements from job_application.csv
    """
    
    # Foreign key references - positioned right after the implicit id field
    job = models.ForeignKey(
        'JobPosting', 
        on_delete=models.CASCADE, 
        related_name='applications',
        help_text="Foreign key to job_posting.id"
    )
    freelancer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='job_applications',
        help_text="Foreign key to freelancer_profile.id (using User model)"
    )
    
    # Application details
    resume = models.URLField(
        max_length=500,
        help_text="URL to the freelancer's resume"
    )
    cover_letter = models.TextField(
        help_text="Cover letter submitted by freelancer"
    )
    expected_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Freelancer's expected rate"
    )
    
    # Application status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Application status (Pending, Accepted, Rejected)"
    )
    
    # Metadata
    date_applied = models.DateTimeField(
        auto_now_add=True,
        help_text="Date the freelancer applied"
    )
    
    class Meta:
        db_table = 'job_application'
        ordering = ['-date_applied']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        # Ensure a freelancer can only apply once to the same job
        unique_together = ['job', 'freelancer']
    
    
    def __str__(self):
        return f"{self.freelancer.username} - {self.job.job_title}"
    
    @property
    def is_pending(self):
        """Check if the application is still pending"""
        return self.status == 'pending'
    
    @property
    def is_accepted(self):
        """Check if the application has been accepted"""
        return self.status == 'accepted'
    
    @property
    def is_rejected(self):
        """Check if the application has been rejected"""
        return self.status == 'rejected'


class JobPosting(models.Model):
    """
    Job posting model based on the requirements from Table.csv
    """
    
    # Job provider reference (assuming it's from another app/model)
    job_provider_id = models.IntegerField(help_text="Foreign key to job_provider_profile.id")
    
    # Basic job information
    job_title = models.CharField(max_length=255, help_text="Job title")
    department = models.CharField(max_length=100, help_text="Department or team the job belongs to")
    job_type = models.CharField(
        max_length=50, 
        choices=[
            ('full-time', 'Full-time'),
            ('part-time', 'Part-time'),
            ('contract', 'Contract'),
            ('internship', 'Internship'),
            ('temporary', 'Temporary'),
        ],
        help_text="Job type"
    )
    work_location = models.CharField(max_length=255, help_text="Work area")
    work_mode = models.CharField(
        max_length=20,
        choices=[
            ('on-site', 'On-site'),
            ('remote', 'Remote'),
            ('hybrid', 'Hybrid'),
        ],
        help_text="Mode of work"
    )
    
    # Job details
    role_overview = models.TextField(help_text="Overview of the job role")
    key_responsibilities = models.TextField(help_text="List of key responsibilities")
    required_qualifications = models.TextField(help_text="Minimum qualifications required")
    preferred_qualifications = models.TextField(blank=True, null=True, help_text="Preferred qualifications")
    languages_required = models.CharField(max_length=255, blank=True, null=True, help_text="Required languages")
    job_category = models.CharField(
        max_length=100,
        choices=[
            ('engineering', 'Engineering'),
            ('marketing', 'Marketing'),
            ('sales', 'Sales'),
            ('hr', 'Human Resources'),
            ('finance', 'Finance'),
            ('operations', 'Operations'),
            ('design', 'Design'),
            ('product', 'Product'),
            ('customer-support', 'Customer Support'),
            ('other', 'Other'),
        ],
        help_text="Job category"
    )
    
    # Salary information
    salary_from = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Minimum salary"
    )
    salary_to = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Maximum salary"
    )
    currency = models.CharField(
        max_length=3,
        choices=[
            ('USD', 'USD'),
            ('AED', 'AED'),
            ('EUR', 'EUR'),
            ('GBP', 'GBP'),
        ],
        default='USD',
        help_text="Currency"
    )
    
    # Application details
    application_deadline = models.DateTimeField(blank=True, null=True, help_text="Deadline to apply")
    application_method = models.CharField(
        max_length=20,
        choices=[
            ('portal', 'Portal'),
            ('email', 'Email'),
        ],
        default='portal',
        help_text="Application method"
    )
    interview_mode = models.CharField(
        max_length=20,
        choices=[
            ('in-person', 'In-person'),
            ('zoom', 'Zoom'),
            ('phone', 'Phone'),
            ('hybrid', 'Hybrid'),
        ],
        help_text="Interview mode"
    )
    hiring_manager = models.CharField(max_length=255, help_text="Name of the hiring manager")
    number_of_openings = models.IntegerField(default=1, help_text="Number of open positions")
    expected_start_date = models.DateTimeField(blank=True, null=True, help_text="Expected start date")
    
    # Additional information
    screening_questions = models.TextField(blank=True, null=True, help_text="Screening questions for applicants")
    file_upload = models.URLField(blank=True, null=True, help_text="URL for job-related file upload")
    
    # Benefits
    health_insurance = models.BooleanField(default=False, help_text="Health insurance offered?")
    remote_work = models.BooleanField(default=False, help_text="Remote work allowed?")
    paid_leave = models.BooleanField(default=False, help_text="Number of Paid leaves offered?")
    bonus = models.BooleanField(default=False, help_text="Bonus offered?")
    
    # Metadata
    date_posted = models.DateTimeField(auto_now_add=True, help_text="Date the job was posted")
    job_status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('filled', 'Filled'),
            ('paused', 'Paused'),
        ],
        default='open',
        help_text="Job status"
    )
    
    class Meta:
        db_table = 'job_posting'
        ordering = ['-date_posted']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.job_title} - {self.department}"
    
    @property
    def is_active(self):
        """Check if the job posting is currently active"""
        return self.job_status == 'open'
    
    @property
    def salary_range(self):
        """Return formatted salary range"""
        if self.salary_from and self.salary_to:
            return f"{self.currency} {self.salary_from:,.0f} - {self.salary_to:,.0f}"
        elif self.salary_from:
            return f"{self.currency} {self.salary_from:,.0f}+"
        return "Salary not specified"