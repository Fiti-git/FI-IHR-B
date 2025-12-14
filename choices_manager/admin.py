from django.contrib import admin
from .models import ChoiceGroup, ChoiceItem


class ChoiceItemInline(admin.TabularInline):
    model = ChoiceItem
    extra = 1
    fields = ('label', 'value', 'sort_order', 'is_active')
    ordering = ('sort_order',)
    show_change_link = True


@admin.register(ChoiceGroup)
class ChoiceGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    inlines = [ChoiceItemInline]
    ordering = ('name',)

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(ChoiceItem)
class ChoiceItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'group', 'sort_order', 'is_active')
    list_filter = ('group', 'is_active')
    search_fields = ('label', 'value')
    ordering = ('group', 'sort_order')
