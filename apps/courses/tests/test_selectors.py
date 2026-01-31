# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for courses selectors."""

import pytest

from apps.courses.selectors import get_course_by_uuid, get_published_courses
from apps.courses.tests.factories import CourseFactory, CourseLessonFactory
from apps.lessons.tests.factories import LessonFactory


@pytest.mark.django_db
def test_get_published_courses_excludes_unpublished() -> None:
    CourseFactory.create(title="Published", is_published=True)
    CourseFactory.create(title="Unpublished", is_published=False)

    courses = get_published_courses()

    assert courses.count() == 1
    course = courses.first()
    assert course
    assert course.title == "Published"


@pytest.mark.django_db
def test_get_course_by_uuid() -> None:
    course = CourseFactory.create(title="Test Course")

    result = get_course_by_uuid(str(course.uuid))

    assert result is not None
    assert result.title == "Test Course"


@pytest.mark.django_db
def test_get_course_by_uuid_returns_none_for_unpublished() -> None:
    course = CourseFactory.create(is_published=False)

    result = get_course_by_uuid(str(course.uuid))

    assert result is None


@pytest.mark.django_db
def test_get_course_by_uuid_filters_unpublished_lessons() -> None:
    published_lesson = LessonFactory.create(title="Published", is_published=True)
    unpublished_lesson = LessonFactory.create(title="Unpublished", is_published=False)
    course = CourseFactory.create()
    CourseLessonFactory.create(course=course, lesson=published_lesson, order=1)
    CourseLessonFactory.create(course=course, lesson=unpublished_lesson, order=2)

    result = get_course_by_uuid(str(course.uuid))

    assert result is not None
    lesson_titles = [cl.lesson.title for cl in result.course_lessons.all()]
    assert lesson_titles == ["Published"]
