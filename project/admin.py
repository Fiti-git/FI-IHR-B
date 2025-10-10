from django.contrib import admin
from .models import Project, Proposal, Milestone, MilestonePayment, Feedback, ProjectTag


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'category', 'budget', 'project_type', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'project_type', 'visibility', 'category', 'created_at']
    search_fields = ['title', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Project Details', {
            'fields': ('budget', 'project_type', 'deadline', 'visibility', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'freelancer', 'budget', 'status', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['project__title', 'freelancer__username', 'cover_letter']
    readonly_fields = ['submitted_at', 'updated_at']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Proposal Information', {
            'fields': ('project', 'freelancer', 'budget', 'cover_letter', 'status')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'project', 'freelancer', 'budget', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'project__title', 'freelancer__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    ordering = ['start_date']
    
    fieldsets = (
        ('Milestone Information', {
            'fields': ('project', 'freelancer', 'name', 'description', 'budget', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MilestonePayment)
class MilestonePaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'milestone', 'project', 'freelancer', 'payment_amount', 'payment_status', 'payment_date', 'released_at']
    list_filter = ['payment_status', 'payment_method', 'payment_date', 'released_at']
    search_fields = ['milestone__name', 'project__title', 'freelancer__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'payment_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('milestone', 'project', 'freelancer', 'payment_amount', 'payment_method')
        }),
        ('Payment Status', {
            'fields': ('payment_status', 'payment_date', 'released_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'client', 'freelancer', 'rating', 'submitted_at']
    list_filter = ['rating', 'submitted_at']
    search_fields = ['project__title', 'client__username', 'freelancer__username', 'feedback']
    readonly_fields = ['submitted_at']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('project', 'client', 'freelancer', 'rating', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'tag']
    list_filter = ['tag']
    search_fields = ['project__title', 'tag']
    ordering = ['project', 'tag']