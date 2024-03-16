"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # alias to prevent confusion from original

from . import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    # all variables below are built in BaseUserAdmin variables
    ordering = ['id']  # order users by id
    list_display = ['email', 'name']  # display email and name columns


admin.site.register(models.User, UserAdmin)  # this to register the given model(s) with the given admin class