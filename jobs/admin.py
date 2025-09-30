from django.contrib import admin
from .models import JobPosting, JobApplication, JobInterview


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    """
    Admin interface for JobPosting model
    """
    list_display = [
        'job_title', 
        'department', 
        'job_type', 
        'work_mode', 
        'job_status', 
        'number_of_openings',
        'date_posted',
        'application_deadline'
    ]
    
    list_filter = [
        'job_type',
        'work_mode', 
        'job_category',
        'job_status',
        'currency',
        'health_insurance',
        'remote_work',
        'paid_leave',
        'bonus',
        'date_posted'
    ]
    
    search_fields = [
        'job_title',
        'department', 
        'work_location',
        'hiring_manager',
        'role_overview',
        'key_responsibilities'
    ]
    
    readonly_fields = ['date_posted']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'job_title',
                'department', 
                'job_provider_id',
                'job_type',
                'job_category',
                'work_location',
                'work_mode',
                'number_of_openings'
            )
        }),
        ('Job Details', {
            'fields': (
                'role_overview',
                'key_responsibilities', 
                'required_qualifications',
                'preferred_qualifications',
                'languages_required'
            )
        }),
        ('Salary & Benefits', {
            'fields': (
                'salary_from',
                'salary_to',
                'currency',
                'health_insurance',
                'remote_work', 
                'paid_leave',
                'bonus'
            )
        }),
        ('Application Process', {
            'fields': (
                'application_method',
                'application_deadline',
                'interview_mode',
                'hiring_manager',
                'expected_start_date',
                'screening_questions',
                'file_upload'
            )
        }),
        ('Status & Metadata', {
            'fields': (
                'job_status',
                'date_posted'
            )
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make date_posted readonly for existing objects"""
        if obj:  # editing an existing object
            return self.readonly_fields + ['date_posted']
        return self.readonly_fields


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for JobApplication model
    """
    list_display = [
        'id',
        'job',
        'freelancer_id',
        'status',
        'expected_rate',
        'date_applied'
    ]
    
    list_filter = [
        'status',
        'date_applied',
        'job__job_type',
        'job__job_category'
    ]
    
    search_fields = [
        'freelancer_id',
        'job__job_title',
        'job__department'
    ]
    
    readonly_fields = ['date_applied']
    
    fieldsets = (
        ('Application Information', {
            'fields': (
                'job',
                'freelancer_id',
                'status'
            )
        }),
        ('Application Details', {
            'fields': (
                'resume',
                'cover_letter',
                'expected_rate'
            )
        }),
        ('Metadata', {
            'fields': (
                'date_applied',
            )
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing objects"""
        if obj:  # editing an existing object
            return self.readonly_fields + ['job', 'freelancer_id', 'date_applied']
        return self.readonly_fields


@admin.register(JobInterview)
class JobInterviewAdmin(admin.ModelAdmin):
    """
    Admin interface for JobInterview model
    """
    list_display = [
        'id',
        'application',
        'interview_date',
        'interview_mode',
        'status'
    ]
    
    list_filter = [
        'status',
        'interview_mode',
        'interview_date',
        'application__job__job_type'
    ]
    
    search_fields = [
        'application__job__job_title',
        'application__freelancer_id',
        'interview_notes'
    ]
    
    readonly_fields = []
    
    fieldsets = (
        ('Interview Information', {
            'fields': (
                'application',
                'interview_date',
                'interview_mode',
                'status'
            )
        }),
        ('Interview Details', {
            'fields': (
                'interview_notes',
            )
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make application field readonly when editing"""
        if obj:  # editing an existing object
            return ['application']
        return []