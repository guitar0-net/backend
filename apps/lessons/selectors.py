# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the lessons app."""

from django.db.models import Prefetch, QuerySet

from apps.lessons.models import Lesson


def get_published_lessons() -> QuerySet[Lesson]:
    """Get a QuerySet of all published Lesson objects.

    Returns:
        QuerySet[Lesson]: QuerySet of all published lessons
    """
    return (
        Lesson.objects
        .filter(is_published=True)
        .order_by("id")
        .prefetch_related("songs")
    )


def get_lesson_by_uuid(uuid: str) -> Lesson | None:
    """Get a single published Lesson by UUID with related data.

    Returns:
        Lesson or None if not found.
    """
    return (
        Lesson.objects
        .filter(uuid=uuid, is_published=True)
        .prefetch_related(
            "songs__chords",
            "songs__schemes",
            Prefetch(
                "addition_lessons",
                queryset=Lesson.objects.filter(is_published=True),
            ),
        )
        .first()
    )
