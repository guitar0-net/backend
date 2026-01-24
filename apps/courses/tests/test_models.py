# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for Course and CourseLesson models."""

import pytest
from django.db import IntegrityError

from apps.courses.models import Course, CourseLesson
from apps.courses.tests.factories import CourseFactory, CourseLessonFactory
from apps.lessons.tests.factories import LessonFactory


@pytest.mark.django_db
def test_course_factory_creates_course() -> None:
    course = CourseFactory.create()

    assert course.pk is not None
    assert course.title
    assert course.uuid
    assert course.created_at
    assert course.updated_at


@pytest.mark.django_db
def test_course_str_method() -> None:
    course = CourseFactory.create(title="Beginner Guitar")

    assert str(course) == "Beginner Guitar"


@pytest.mark.django_db
def test_course_default_fields() -> None:
    course = Course()

    assert course.is_published is True


@pytest.mark.django_db
def test_course_without_lessons() -> None:
    course = CourseFactory.create()

    assert course.lessons.count() == 0


@pytest.mark.django_db
def test_course_lessons_ordering() -> None:
    course = CourseFactory.create()
    lesson1 = LessonFactory.create(title="First")
    lesson2 = LessonFactory.create(title="Second")
    CourseLessonFactory.create(course=course, lesson=lesson2, order=2)
    CourseLessonFactory.create(course=course, lesson=lesson1, order=1)

    ordered = list(course.course_lessons.values_list("lesson__title", flat=True))

    assert ordered == ["First", "Second"]


@pytest.mark.django_db
def test_course_lesson_str_method() -> None:
    course = CourseFactory.create(title="Course 1")
    lesson = LessonFactory.create(title="Intro")
    cl = CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    assert str(cl) == "Lesson # 1 Intro in Course 1"


@pytest.mark.django_db
def test_course_lesson_unique_course_lesson() -> None:
    lesson = LessonFactory.create()
    course = CourseFactory.create()
    CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    with pytest.raises(IntegrityError):
        CourseLessonFactory.create(course=course, lesson=lesson, order=2)


@pytest.mark.django_db
def test_course_lesson_unique_course_order() -> None:
    course = CourseFactory.create()
    CourseLessonFactory.create(course=course, order=1)

    with pytest.raises(IntegrityError):
        CourseLessonFactory.create(course=course, order=1)


@pytest.mark.django_db
def test_course_cascade_delete() -> None:
    course = CourseFactory.create(lessons=2)
    course_id = course.pk

    assert CourseLesson.objects.filter(course_id=course_id).count() == 2

    course.delete()

    assert CourseLesson.objects.filter(course_id=course_id).count() == 0
