"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # alias to prevent confusion from original
from django.utils.translation import gettext_lazy as _  # this translates the text across all django config; RESEARCH

from . import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    # all variables below are built in BaseUserAdmin variables
    # ordering, list_display for main all Users list page
    ordering = ['id']  # order users by id
    list_display = ['email', 'name']  # display email and name columns
    # fieldsets for the edit/change User page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # None refers to the title, so no title, and the fields to include in the user edit/change page ie email, password
        (
            _('Permissions'),  # name of the title for this section is permissions
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']  # makes this field read only, no editing
    # fieldsets for the add User page
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),  # 'classes' in django docs to modify css
                'fields': (
                    'email',
                    'password1',  # for pwd django default
                    'password2',  # for pwd confirmation
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
    )


admin.site.register(models.User, UserAdmin)  # this to register the given model(s) with the given admin class