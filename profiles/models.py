from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class FreelancerProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
    ]

    SPECIALIZATION_CHOICES = [
        ('web-dev', 'Web Development'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
    ]

    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('arabic', 'Arabic'),
        ('french', 'French'),
        ('spanish', 'Spanish'),
    ]

    LANGUAGE_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('fluent', 'Fluent'),
    ]

    HOURLY_RATE_CHOICES = [
        ('30', '$30/hr'),
        ('40', '$40/hr'),
        ('50', '$50/hr'),
        ('60', '$60/hr'),
        ('70', '$70/hr'),
    ]

    COUNTRY_CHOICES = [
        ('uae', 'UAE'),
        ('uk', 'UK'),
        ('usa', 'USA'),
        ('india', 'India'),
    ]

    CITY_CHOICES = [
        ('dubai', 'Dubai'),
        ('london', 'London'),
        ('new-york', 'New York'),
        ('toronto', 'Toronto'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    full_name = models.CharField(max_length=100 , null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    professional_title = models.CharField(max_length=100 , null=True, blank=True)
    hourly_rate = models.CharField(max_length=10, choices=HOURLY_RATE_CHOICES, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_LEVEL_CHOICES, null=True, blank=True)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, null=True, blank=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES, null=True, blank=True)
    city = models.CharField(max_length=20, choices=CITY_CHOICES, null=True, blank=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, null=True, blank=True)
    language_proficiency = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES, null=True, blank=True)
    linkedin_or_github = models.URLField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    education = models.JSONField(
        null=True, 
        blank=True, 
        default=list, 
        help_text="A list of education entries, e.g., [{'degree': 'B.Sc.', 'school': 'MIT', 'start_year': '2018', 'end_year': '2022', 'description': '...'}]"
    )
    work_experience = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text="A list of work experience entries, e.g., [{'job_title': 'UX Designer', 'company': 'Dropbox', 'start_year': '2020', 'end_year': '2022', 'description': '...'}]"
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username}'s Freelancer Profile"


class JobProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_provider_profile')
    
    # Profile image (store as a file field, you might want to specify upload_to and max_size)
    profile_image = models.ImageField(upload_to='job_provider_profiles/', blank=True, null=True)
    
    # Company Name or Job Provider's Name
    company_name = models.CharField(max_length=255)
    
    # Email address (you might already have this in the User model, but adding it here if needed)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    
    # Phone number
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Company Overview (Description)
    company_overview = models.TextField(blank=True, null=True)
    
    # Job Type options: Full-time, Part-time, Remote
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('remote', 'Remote'),
    ]
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full-time')
    
    # Industry options
    INDUSTRY_CHOICES = [
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
    ]
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='technology')
    
    # Country options (you might want to use a Country model for a more extensive list)
    COUNTRY_CHOICES = [
        ('usa', 'United States'),
        ('canada', 'Canada'),
        ('uk', 'United Kingdom'),
    ]
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES, default='usa')
    
    # Add any additional fields here if needed (for example, social media, website URL, etc.)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"{self.company_name} - Profile"
    
    class Meta:
        verbose_name = "Job Provider Profile"
        verbose_name_plural = "Job Provider Profiles"
