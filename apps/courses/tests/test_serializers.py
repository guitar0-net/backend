# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for courses serializers."""

import pytest

from apps.courses.api.v1.serializers.course_detail_serializer import (
    CourseDetailSerializer,
)
from apps.courses.api.v1.serializers.courses_list_serializer import (
    CoursesListSerializer,
)
from apps.courses.selectors import get_published_courses
from apps.courses.tests.factories import CourseFactory, CourseLessonFactory
from apps.lessons.tests.factories import LessonFactory


@pytest.mark.django_db
def test_courses_list_serializer_fields() -> None:
    """CoursesListSerializer includes expected fields."""
    lesson = LessonFactory.create(title="Lesson 1")
    course = CourseFactory.create(title="Course", description="Desc")
    CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    course_from_selector = get_published_courses().get(pk=course.pk)
    serializer = CoursesListSerializer(course_from_selector)
    data = serializer.data

    assert data["uuid"] == str(course.uuid)
    assert data["title"] == "Course"
    assert data["description"] == "Desc"
    assert data["lessons_count"] == 1


@pytest.mark.django_db
def test_courses_list_serializer_counts_only_published_lessons() -> None:
    """CoursesListSerializer counts only published lessons."""
    course = CourseFactory.create()
    published = LessonFactory.create(is_published=True)
    unpublished = LessonFactory.create(is_published=False)
    CourseLessonFactory.create(course=course, lesson=published, order=1)
    CourseLessonFactory.create(course=course, lesson=unpublished, order=2)

    course_from_selector = get_published_courses().get(pk=course.pk)
    serializer = CoursesListSerializer(course_from_selector)
    data = serializer.data

    assert data["lessons_count"] == 1


@pytest.mark.django_db
def test_course_detail_serializer_fields() -> None:
    """CourseDetailSerializer includes expected fields."""
    lesson = LessonFactory.create(title="Lesson 1")
    course = CourseFactory.create(title="Course", description="Desc")
    CourseLessonFactory.create(course=course, lesson=lesson, order=1)

    serializer = CourseDetailSerializer(course)
    data = serializer.data

    assert data["uuid"] == str(course.uuid)
    assert data["title"] == "Course"
    assert data["description"] == "Desc"
    assert "created_at" in data
    assert "updated_at" in data
    assert len(data["lessons"]) == 1
    assert data["lessons"][0]["order"] == 1
    assert data["lessons"][0]["lesson"]["title"] == "Lesson 1"


@pytest.mark.django_db
def test_course_detail_serializer_lessons_order() -> None:
    """Lessons are returned in order."""
    course = CourseFactory.create()
    lesson1 = LessonFactory.create(title="First")
    lesson2 = LessonFactory.create(title="Second")
    CourseLessonFactory.create(course=course, lesson=lesson2, order=2)
    CourseLessonFactory.create(course=course, lesson=lesson1, order=1)

    serializer = CourseDetailSerializer(course)
    data = serializer.data

    assert data["lessons"][0]["lesson"]["title"] == "First"
    assert data["lessons"][1]["lesson"]["title"] == "Second"
