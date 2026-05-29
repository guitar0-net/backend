# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the sync app."""

import uuid
from datetime import datetime

from django.db.models import Max, QuerySet

from apps.courses.models import Course, CourseLesson
from apps.lessons.models import Lesson


def get_lessons_for_sync(since: datetime | None = None) -> QuerySet[Lesson]:
    """Return published lessons with all related data prefetched for sync.

    When `since` is provided, only lessons whose updated_at is strictly after
    that timestamp are returned — enabling delta sync on the client.
    """
    qs = (
        Lesson.objects
        .filter(is_published=True)
        .order_by("updated_at")
        .prefetch_related(
            "songs__chords",
            "songs__schemes",
        )
    )
    if since is not None:
        qs = qs.filter(updated_at__gt=since)
    return qs


def get_published_lesson_uuids() -> list[uuid.UUID]:
    """Return UUIDs of all currently published lessons.

    The client uses this to prune lessons that were unpublished or deleted
    since the last sync.
    """
    return list(Lesson.objects.filter(is_published=True).values_list("uuid", flat=True))


def get_courses_for_sync() -> QuerySet[Course]:
    """Return published courses ordered by updated_at.

    Always the full set — no delta filtering — since course membership changes
    do not bump Lesson.updated_at.
    """
    return Course.objects.filter(is_published=True).order_by("updated_at")


def get_course_lessons_for_sync() -> QuerySet[CourseLesson]:
    """Return published course-lesson memberships.

    Filters both course and lesson to is_published=True.
    select_related ensures course.uuid and lesson.uuid resolve without extra queries.
    """
    return (
        CourseLesson.objects
        .filter(course__is_published=True, lesson__is_published=True)
        .select_related("course", "lesson")
        .order_by("course__updated_at", "order")
    )


def get_published_course_uuids() -> list[uuid.UUID]:
    """Return UUIDs of all currently published courses.

    The client uses this to prune courses that were unpublished or deleted
    since the last sync.
    """
    return list(Course.objects.filter(is_published=True).values_list("uuid", flat=True))


def get_content_version() -> str | None:
    """Return the latest lesson updated_at as an ISO-8601 string.

    Returns None when there are no published lessons.
    The client stores this value and compares it on next launch to decide
    whether a sync is needed at all.
    """
    result = Lesson.objects.filter(is_published=True).aggregate(
        version=Max("updated_at")
    )
    ts = result["version"]
    return ts.isoformat() if ts is not None else None
