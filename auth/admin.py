from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Permission
from django import forms
from django.utils.translation import gettext_lazy as _
from collections import defaultdict


class GroupedPermissionWidget(forms.CheckboxSelectMultiple):
    """
    Custom widget to display grouped permissions by app_label and model.
    """

    def optgroups(self, name, value, attrs=None):
        # Group permissions by app_label and model
        permissions = self.choices.queryset if hasattr(self.choices, 'queryset') else []
        grouped = defaultdict(list)
        for perm in permissions:
            group_label = f"{perm.content_type.app_label} | {perm.content_type.model}"
            grouped[group_label].append((perm.pk, perm.name))

        # Build optgroups for each group_label
        optgroups = []
        for group_label, perms in sorted(grouped.items()):
            options = []
            for pk, label in perms:
                selected = str(pk) in value
                options.append(self.create_option(name, str(pk), label, selected, False, None))
            optgroups.append((group_label, options, 0))
        return optgroups


class CustomUserChangeForm(forms.ModelForm):
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'content_type__model', 'codename'),
        required=False,
        widget=GroupedPermissionWidget,
        label=_("User permissions"),
    )

    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm

    filter_horizontal = ('groups',)  # Keep groups with default widget

    # Optional: customize list_display, fieldsets, etc as needed

    # If you want to customize the UserAdmin fieldsets to include user_permissions as checkbox group:
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
