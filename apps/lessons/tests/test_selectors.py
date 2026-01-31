# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lessons selectors."""

import pytest

from apps.lessons.selectors import get_lesson_by_uuid, get_published_lessons
from apps.lessons.tests.factories import LessonFactory


@pytest.mark.django_db
def test_get_published_lessons_excludes_unpublished() -> None:
    LessonFactory.create(title="Published", is_published=True)
    LessonFactory.create(title="Unpublished", is_published=False)

    lessons = get_published_lessons()

    assert lessons.count() == 1
    lesson = lessons.first()
    assert lesson
    assert lesson.title == "Published"


@pytest.mark.django_db
def test_get_lesson_by_uuid() -> None:
    lesson = LessonFactory.create(title="Test Lesson")

    result = get_lesson_by_uuid(str(lesson.uuid))

    assert result is not None
    assert result.title == "Test Lesson"


@pytest.mark.django_db
def test_get_lesson_by_uuid_returns_none_for_unpublished() -> None:
    lesson = LessonFactory.create(is_published=False)

    result = get_lesson_by_uuid(str(lesson.uuid))

    assert result is None


@pytest.mark.django_db
def test_get_lesson_by_uuid_filters_unpublished_addition_lessons() -> None:
    published = LessonFactory.create(title="Published", is_published=True)
    unpublished = LessonFactory.create(title="Unpublished", is_published=False)
    lesson = LessonFactory.create(addition_lessons=[published, unpublished])

    result = get_lesson_by_uuid(str(lesson.uuid))

    assert result is not None
    addition_titles = [lesson.title for lesson in result.addition_lessons.all()]
    assert addition_titles == ["Published"]
