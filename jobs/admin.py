from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import (
    JobPosting,
    JobApplication,
    JobInterview,
    JobOffer,
    ApplicationWithdrawal,
)

from profiles.models import FreelancerProfile


# =====================================================
# MIXINS
# =====================================================
class JobStatusActionMixin:
    """Common job status actions"""

    @admin.action(description="Mark selected jobs as Open")
    def mark_open(self, request, queryset):
        queryset.update(job_status="open")

    @admin.action(description="Mark selected jobs as Closed")
    def mark_closed(self, request, queryset):
        queryset.update(job_status="closed")


# =====================================================
# JOB POSTINGS
# =====================================================
@admin.register(JobPosting)
class JobPostingAdmin(JobStatusActionMixin, admin.ModelAdmin):
    verbose_name = "Job"
    verbose_name_plural = "Jobs"

    list_display = (
        "job_title",
        "department",
        "employer_link",
        "job_type",
        "work_mode",
        "job_status",
        "date_posted",
        "number_of_openings",
    )

    list_filter = (
        "job_type",
        "work_mode",
        "job_status",
        "department",
    )

    search_fields = (
        "job_title",
        "department",
        "job_provider__company_name",
    )

    ordering = ("-date_posted",)
    list_per_page = 25
    actions = ["mark_open", "mark_closed"]

    readonly_fields = ("date_posted",)

    fieldsets = (
        ("Job Details", {
            "fields": (
                "job_provider",
                "job_title",
                "department",
                "job_type",
                "work_location",
                "work_mode",
                "job_category",
                "number_of_openings",
                "expected_start_date",
            )
        }),
        ("Description", {
            "fields": (
                "role_overview",
                "key_responsibilities",
                "required_qualifications",
                "preferred_qualifications",
                "languages_required",
            )
        }),
        ("Salary & Benefits", {
            "fields": (
                "salary_from",
                "salary_to",
                "currency",
                "health_insurance",
                "remote_work",
                "paid_leave",
                "bonus",
            )
        }),
        ("Application & Interview", {
            "fields": (
                "application_deadline",
                "application_method",
                "interview_mode",
                "hiring_manager",
                "screening_questions",
                "file_upload",
            )
        }),
        ("Status", {
            "fields": ("job_status", "date_posted")
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("job_provider")

    def employer_link(self, obj):
        if not obj.job_provider:
            return "—"
        url = reverse(
            "admin:profiles_jobproviderprofile_change",
            args=[obj.job_provider.id],
        )
        return format_html('<a href="{}">{}</a>', url, obj.job_provider.company_name)

    employer_link.short_description = "Employer"


# =====================================================
# JOB APPLICATIONS
# =====================================================
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    verbose_name = "Job Application"
    verbose_name_plural = "Job Applications"

    list_display = (
        "id",
        "job_link",
        "candidate_link",
        "candidate_title",
        "status",
        "expected_rate",
        "date_applied",
        "rating",
        "resume_link",
        "cover_letter_preview",
    )

    list_filter = ("status",)
    search_fields = ("job__job_title", "freelancer_id__user__username")
    ordering = ("-date_applied",)
    list_per_page = 25

    readonly_fields = ("date_applied",)

    fieldsets = (
        ("Application Details", {
            "fields": (
                "job",
                "freelancer_id",
                "resume",
                "cover_letter",
                "expected_rate",
                "status",
                "rating",
                "comments",
            )
        }),
    )

    # ---------- LINKS & PROFILE DATA ----------

    def job_link(self, obj):
        if not obj.job:
            return "—"
        url = reverse("admin:jobs_jobposting_change", args=[obj.job.id])
        return format_html('<a href="{}">{}</a>', url, obj.job.job_title)

    job_link.short_description = "Job"

    def candidate_link(self, obj):
        profile = obj.freelancer_id
        if not profile:
            return "—"

        url = reverse(
            "admin:profiles_freelancerprofile_change",
            args=[profile.id],
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            profile.full_name or profile.user.username,
        )

    candidate_link.short_description = "Candidate"

    def candidate_title(self, obj):
        profile = obj.freelancer_id
        return profile.professional_title if profile else "—"

    candidate_title.short_description = "Title"

    def resume_link(self, obj):
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">Download</a>',
                obj.resume.url
            )
        return "—"

    resume_link.short_description = "Resume"

    def cover_letter_preview(self, obj):
        if not obj.cover_letter:
            return "—"
        return obj.cover_letter[:50] + ("..." if len(obj.cover_letter) > 50 else "")

    cover_letter_preview.short_description = "Cover Letter"

# =====================================================
# INTERVIEWS
# =====================================================
@admin.register(JobInterview)
class JobInterviewAdmin(admin.ModelAdmin):
    list_display = (
        "application_link",
        "interview_date",
        "interview_mode",
        "status",
        "rating",
    )

    list_filter = ("interview_mode", "status")
    search_fields = ("application__job__job_title",)
    ordering = ("-interview_date",)
    list_per_page = 25

    def application_link(self, obj):
        if not obj.application:
            return "—"
        url = reverse("admin:jobs_jobapplication_change", args=[obj.application.id])
        return format_html('<a href="{}">Application #{}</a>', url, obj.application.id)

    application_link.short_description = "Application"


# =====================================================
# OFFERS
# =====================================================
@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = (
        "application_link",
        "offer_status",
        "date_offered",
        "date_accepted",
        "date_rejected",
    )

    list_filter = ("offer_status",)
    search_fields = ("application__job__job_title",)
    ordering = ("-date_offered",)
    list_per_page = 25

    def application_link(self, obj):
        if not obj.application:
            return "—"
        url = reverse("admin:jobs_jobapplication_change", args=[obj.application.id])
        return format_html('<a href="{}">Application #{}</a>', url, obj.application.id)

    application_link.short_description = "Application"


# =====================================================
# WITHDRAWALS
# =====================================================
@admin.register(ApplicationWithdrawal)
class ApplicationWithdrawalAdmin(admin.ModelAdmin):
    list_display = (
        "application_link",
        "withdrawal_date",
        "reason",
    )

    search_fields = ("application__job__job_title", "reason")
    ordering = ("-withdrawal_date",)
    list_per_page = 25

    def application_link(self, obj):
        if not obj.application:
            return "—"
        url = reverse("admin:jobs_jobapplication_change", args=[obj.application.id])
        return format_html('<a href="{}">Application #{}</a>', url, obj.application.id)

    application_link.short_description = "Application"
