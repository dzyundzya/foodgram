from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    filter_fields = (
        'is_active',
        'is_superuser',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
