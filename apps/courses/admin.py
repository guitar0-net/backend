# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later


"""Admin settings for courses."""

from django.contrib import admin

from apps.courses.models import Course, CourseLesson


class CourseLessonInline(admin.TabularInline):  # type: ignore[type-arg]
    """Inline for managing lessons within a course."""

    model = CourseLesson
    extra = 1
    autocomplete_fields = ("lesson",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Admin interface for the Course model."""

    list_display = ("title", "is_published")
    search_fields = ("title",)
    inlines = (CourseLessonInline,)
