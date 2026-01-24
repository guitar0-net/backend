# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later


"""Admin settings for lessons."""

from django.contrib import admin

from apps.lessons.models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Admin interface for the Lesson model."""

    list_display = ("title", "is_published")
    search_fields = ("title",)
