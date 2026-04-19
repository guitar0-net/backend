# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin settings for announcements."""

from collections.abc import Sequence
from typing import ClassVar

from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin  # type: ignore[import-untyped]

from apps.announcements.models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(MarkdownxModelAdmin):  # type: ignore[misc]
    """Admin interface for the Announcement model."""

    list_display = (
        "title",
        "slug",
        "product_version",
        "published_at",
        "created_at",
    )
    list_filter = ("published_at",)
    search_fields = ("title", "slug", "product_version")
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug": ("title",)}
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-published_at", "-created_at")
    date_hierarchy = "published_at"
