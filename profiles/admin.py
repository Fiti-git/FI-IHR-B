from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils.html import format_html

from .models import FreelancerProfile, JobProviderProfile

