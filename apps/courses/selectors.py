# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the courses app."""

from django.db.models import Count, Prefetch, Q, QuerySet

from apps.courses.models import Course, CourseLesson


def get_published_courses() -> QuerySet[Course]:
    """Get a QuerySet of all published Course objects.

    Returns:
        QuerySet[Course]: QuerySet of all published courses with lessons_count
    """
    return (
        Course.objects
        .filter(is_published=True)
        .annotate(
            lessons_count=Count(
                "course_lessons",
                filter=Q(course_lessons__lesson__is_published=True),
            )
        )
        .order_by("id")
    )


def get_course_by_uuid(uuid: str) -> Course | None:
    """Get a single published Course by UUID with related data.

    Returns:
        Course or None if not found.
    """
    return (
        Course.objects
        .filter(uuid=uuid, is_published=True)
        .prefetch_related(
            Prefetch(
                "course_lessons",
                queryset=CourseLesson.objects
                .select_related("lesson")
                .filter(lesson__is_published=True)
                .order_by("order")
                .prefetch_related("lesson__songs"),
            ),
        )
        .first()
    )
