from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import FreelancerProfile, JobProviderProfile
from django.contrib.auth.models import User

# =====================================================
# GLOBAL ADMIN SETTINGS
# =====================================================
admin.site.site_header = "IhrHub Administration"
admin.site.site_title = "IhrHub Admin"
admin.site.index_title = "Operations Dashboard"

# =====================================================
# MIXINS
# =====================================================
class ReadOnlyUserMixin:
    """Prevent changing linked user object"""
    readonly_fields = ('user',)

class SoftActionMixin:
    """Common bulk actions"""
    @admin.action(description="Deactivate selected profiles")
    def deactivate_profiles(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Activate selected profiles")
    def activate_profiles(self, request, queryset):
        queryset.update(is_active=True)

# =====================================================
# FREELANCER PROFILE ADMIN
# =====================================================
@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(ReadOnlyUserMixin, SoftActionMixin, admin.ModelAdmin):
    list_display = (
        'full_name_or_username',
        'user_link',
        'professional_title',
        'experience_level',
        'specialization',
        'country',
        'profile_completion',
        'resume_link',
        'linkedin_link',
        'profile_image_preview',
        'is_verified',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'experience_level',
        'specialization',
        'country',
        'city',
        'gender',
        'is_active',
        'is_verified',
    )

    search_fields = (
        'user__username',
        'user__email',
        'full_name',
        'skills',
    )

    ordering = ('user__username',)
    list_per_page = 25
    actions = ['deactivate_profiles', 'activate_profiles']

    fieldsets = (
        ("User Info", {'fields': ('user', 'full_name', 'phone_number', 'gender')}),
        ("Professional Details", {'fields': ('professional_title', 'experience_level', 'specialization', 'hourly_rate', 'skills', 'bio')}),
        ("Location & Language", {'fields': ('country', 'city', 'language', 'language_proficiency')}),
        ("Documents", {'fields': ('resume', 'linkedin_or_github', 'profile_image')}),
        ("Timestamps & Status", {'fields': ('is_active', 'is_verified', 'created_at', 'updated_at')}),
        ("Education & Work Experience", {'fields': ('education', 'work_experience')}),
    )

    readonly_fields = ('created_at', 'updated_at', 'user')

    # =====================================================
    # QUERY OPTIMIZATION
    # =====================================================
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    # =====================================================
    # DISPLAY HELPERS
    # =====================================================
    def full_name_or_username(self, obj):
        return obj.full_name if obj.full_name else obj.user.username
    full_name_or_username.short_description = "Freelancer"

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"

    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">📄 Download</a>', obj.resume.url)
        return "—"
    resume_link.short_description = "Resume"

    def linkedin_link(self, obj):
        if obj.linkedin_or_github:
            return format_html('<a href="{}" target="_blank">🔗 Profile</a>', obj.linkedin_or_github)
        return "—"
    linkedin_link.short_description = "LinkedIn/GitHub"

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%"/>', obj.profile_image.url)
        return "—"
    profile_image_preview.short_description = "Profile Image"

    def profile_completion(self, obj):
        fields = [
            obj.full_name,
            obj.phone_number,
            obj.professional_title,
            obj.skills,
            obj.bio,
            obj.profile_image,
            obj.resume,
            obj.education,
            obj.work_experience,
        ]
        completed = sum(1 for f in fields if f)
        percent = int((completed / len(fields)) * 100)
        color = "green" if percent >= 80 else "orange" if percent >= 50 else "red"
        return format_html('<strong style="color:{};">{}%</strong>', color, percent)
    profile_completion.short_description = "Completion"


# =====================================================
# JOB PROVIDER PROFILE ADMIN
# =====================================================
@admin.register(JobProviderProfile)
class JobProviderProfileAdmin(ReadOnlyUserMixin, SoftActionMixin, admin.ModelAdmin):
    list_display = (
        'company_name_or_username',
        'user_link',
        'industry',
        'job_type',
        'country',
        'contact_email',
        'profile_image_preview',
        'is_verified',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = ('industry', 'job_type', 'country', 'is_active', 'is_verified')
    search_fields = ('company_name', 'user__username', 'user__email')
    ordering = ('company_name',)
    list_per_page = 25
    actions = ['deactivate_profiles', 'activate_profiles']

    fieldsets = (
        ("User Info", {'fields': ('user', 'company_name', 'phone_number', 'email_address')}),
        ("Company Details", {'fields': ('company_overview', 'industry', 'job_type')}),
        ("Documents", {'fields': ('profile_image',)}),
        ("Timestamps & Status", {'fields': ('is_active', 'is_verified', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at', 'user')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def company_name_or_username(self, obj):
        return obj.company_name if obj.company_name else obj.user.username
    company_name_or_username.short_description = "Job Provider"

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"

    def contact_email(self, obj):
        return obj.email_address or obj.user.email or "—"
    contact_email.short_description = "Email"

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%"/>', obj.profile_image.url)
        return "—"
    profile_image_preview.short_description = "Profile Image"
