from django.db import models
from django.utils.text import slugify


class ChoiceGroup(models.Model):
    """
    A group/category of dynamic choices
    Example: gender, country, job_type, project_status
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ChoiceItem(models.Model):
    """
    Item inside a ChoiceGroup
    Example:
    - group: gender → value: male → label: Male
    - group: job_type → value: full-time → label: Full Time
    """

    group = models.ForeignKey(
        ChoiceGroup,
        on_delete=models.CASCADE,
        related_name="items"
    )

    value = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    sort_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('group', 'value')
        ordering = ['group', 'sort_order', 'label']

    def __str__(self):
        return f"{self.group.slug}: {self.label}"
