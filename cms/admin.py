from django.contrib import admin
from .models import (
    ServiceCategory,
    Service,
    ServiceSubHeading,
    ContactMessage,
)
admin.site.site_header = "Service CMS"
admin.site.site_title = "Service CMS"
admin.site.index_title = "Service Management"

# ----------------------------------
# Inline Sub Headings (Service -> many)
# ----------------------------------
class ServiceSubHeadingInline(admin.TabularInline):
    model = ServiceSubHeading
    extra = 1
    min_num = 0
    fields = ("title", "content", "order")
    ordering = ("order",)


# ----------------------------------
# Service Category Admin
# ----------------------------------
@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


# ----------------------------------
# Service Admin
# ----------------------------------
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name", "header_text")
    autocomplete_fields = ("category",)
    inlines = [ServiceSubHeadingInline]
    ordering = ("-created_at",)


# ----------------------------------
# Contact Message Admin (Inbox style)
# ----------------------------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "created_at",
    )
    search_fields = ("name", "email", "phone")
    list_filter = ("created_at",)

    readonly_fields = (
        "name",
        "email",
        "phone",
        "message",
        "created_at",
    )

    def has_add_permission(self, request):
        return False  # disable manual adding

    def has_change_permission(self, request, obj=None):
        return False  # inbox only

    def has_delete_permission(self, request, obj=None):
        return True  # allow delete
