from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    professional_title = models.CharField(max_length=100, null=True, blank=True)
    hourly_rate = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    experience_level = models.CharField(max_length=20, null=True, blank=True)
    specialization = models.CharField(max_length=50, null=True, blank=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    language_proficiency = models.CharField(max_length=50, null=True, blank=True)
    linkedin_or_github = models.URLField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    education = models.JSONField(null=True, blank=True, default=list)
    work_experience = models.JSONField(null=True, blank=True, default=list)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now)
    role_fillter = models.CharField(max_length=20, default='freelancer')

    def __str__(self):
        return f"{self.user.username}'s Candidate Profile"

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"


class JobProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_provider_profile')
    profile_image = models.ImageField(upload_to='job_provider_profiles/', blank=True, null=True)
    company_name = models.CharField(max_length=255)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    company_overview = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=50, blank=True, null=True)
    industry = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.company_name} - Employer"

    class Meta:
        verbose_name = "Employer"
        verbose_name_plural = "Employers"
