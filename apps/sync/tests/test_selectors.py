# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for sync selectors."""

from datetime import UTC, datetime, timedelta

import pytest

from apps.courses.tests.factories import CourseFactory, CourseLessonFactory
from apps.lessons.models import Lesson
from apps.lessons.tests.factories import LessonFactory
from apps.sync.selectors import (
    get_content_version,
    get_course_lessons_for_sync,
    get_courses_for_sync,
    get_lessons_for_sync,
    get_published_course_uuids,
    get_published_lesson_uuids,
)


@pytest.mark.django_db
def test_get_lessons_for_sync_returns_published_lessons() -> None:
    lesson = LessonFactory.create(is_published=True)

    result = list(get_lessons_for_sync())

    assert lesson in result


@pytest.mark.django_db
def test_get_lessons_for_sync_excludes_unpublished_lessons() -> None:
    LessonFactory.create(is_published=False)

    result = list(get_lessons_for_sync())

    assert result == []


@pytest.mark.django_db
def test_get_lessons_for_sync_with_since_returns_only_newer_lessons() -> None:
    cutoff = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)
    old = LessonFactory.create(is_published=True)
    new = LessonFactory.create(is_published=True)
    Lesson.objects.filter(pk=old.pk).update(updated_at=cutoff - timedelta(days=1))
    Lesson.objects.filter(pk=new.pk).update(updated_at=cutoff + timedelta(days=1))

    result = list(get_lessons_for_sync(since=cutoff))

    assert new in result
    assert old not in result


@pytest.mark.django_db
def test_get_lessons_for_sync_with_since_excludes_exact_cutoff() -> None:
    cutoff = datetime(2026, 3, 10, 8, 0, 0, tzinfo=UTC)
    lesson = LessonFactory.create(is_published=True)
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=cutoff)

    result = list(get_lessons_for_sync(since=cutoff))

    assert result == []


@pytest.mark.django_db
def test_get_published_lesson_uuids_returns_uuids_of_published_lessons() -> None:
    lesson = LessonFactory.create(is_published=True)

    uuids = get_published_lesson_uuids()

    assert lesson.uuid in uuids


@pytest.mark.django_db
def test_get_published_lesson_uuids_excludes_unpublished() -> None:
    LessonFactory.create(is_published=False)

    uuids = get_published_lesson_uuids()

    assert uuids == []


@pytest.mark.django_db
def test_get_content_version_returns_isoformat_string() -> None:
    LessonFactory.create(is_published=True)

    version = get_content_version()

    assert version is not None
    datetime.fromisoformat(version)  # raises if not valid ISO-8601


@pytest.mark.django_db
def test_get_content_version_returns_none_when_no_published_lessons() -> None:
    LessonFactory.create(is_published=False)

    version = get_content_version()

    assert version is None


@pytest.mark.django_db
def test_get_content_version_returns_latest_updated_at() -> None:
    t1 = datetime(2026, 1, 1, tzinfo=UTC)
    t2 = datetime(2026, 6, 1, tzinfo=UTC)
    l1 = LessonFactory.create(is_published=True)
    l2 = LessonFactory.create(is_published=True)
    Lesson.objects.filter(pk=l1.pk).update(updated_at=t1)
    Lesson.objects.filter(pk=l2.pk).update(updated_at=t2)

    version = get_content_version()

    assert version == t2.isoformat()


# =============================================================================
# get_courses_for_sync
# =============================================================================


@pytest.mark.django_db
def test_get_courses_for_sync_returns_published_courses() -> None:
    course = CourseFactory.create(is_published=True)

    result = list(get_courses_for_sync())

    assert course in result


@pytest.mark.django_db
def test_get_courses_for_sync_excludes_unpublished_courses() -> None:
    CourseFactory.create(is_published=False)

    result = list(get_courses_for_sync())

    assert result == []


@pytest.mark.django_db
def test_get_courses_for_sync_returns_course_count() -> None:
    CourseFactory.create(is_published=True)
    CourseFactory.create(is_published=True)

    result = list(get_courses_for_sync())

    assert len(result) == 2


# =============================================================================
# get_published_course_uuids
# =============================================================================


@pytest.mark.django_db
def test_get_published_course_uuids_returns_uuids_of_published_courses() -> None:
    course = CourseFactory.create(is_published=True)

    uuids = get_published_course_uuids()

    assert course.uuid in uuids


@pytest.mark.django_db
def test_get_published_course_uuids_excludes_unpublished() -> None:
    CourseFactory.create(is_published=False)

    uuids = get_published_course_uuids()

    assert uuids == []


# =============================================================================
# get_course_lessons_for_sync
# =============================================================================


@pytest.mark.django_db
def test_get_course_lessons_for_sync_returns_published_memberships() -> None:
    lesson = LessonFactory.create(is_published=True)
    course = CourseFactory.create(is_published=True)
    CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    result = list(get_course_lessons_for_sync())

    assert len(result) == 1
    assert result[0].lesson.uuid == lesson.uuid
    assert result[0].course.uuid == course.uuid


@pytest.mark.django_db
def test_get_course_lessons_for_sync_excludes_unpublished_course() -> None:
    lesson = LessonFactory.create(is_published=True)
    course = CourseFactory.create(is_published=False)
    CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    result = list(get_course_lessons_for_sync())

    assert result == []


@pytest.mark.django_db
def test_get_course_lessons_for_sync_excludes_unpublished_lesson() -> None:
    lesson = LessonFactory.create(is_published=False)
    course = CourseFactory.create(is_published=True)
    CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    result = list(get_course_lessons_for_sync())

    assert result == []
