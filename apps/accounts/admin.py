# SPDX-FileCopyrightText: 2025-2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin interface for users' accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models.social_account import SocialAccount
from apps.accounts.models.user import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):  # type: ignore[type-arg]
    """Users admin interface."""

    list_display = (
        "id",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_display_links = ("email",)
    list_filter = ("is_active",)
    search_fields = ("email",)
    ordering = ("date_joined",)
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_active", "is_staff"),
            },
        ),
    )


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """SocialAccount admin interface."""

    list_display = ("id", "user", "provider", "provider_uid", "created_at")
    list_filter = ("provider",)
    search_fields = ("provider_uid", "user__email")
