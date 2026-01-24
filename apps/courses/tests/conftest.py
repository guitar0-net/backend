# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures for testing courses app."""

import pytest

from apps.courses.models import Course, CourseLesson
from apps.courses.tests.factories import CourseFactory, CourseLessonFactory


@pytest.fixture
def course() -> Course:
    """Fixture creating a course for testing.

    Returns:
        Course: course instance
    """
    return CourseFactory.create()


@pytest.fixture
def course_lesson() -> CourseLesson:
    """Fixture creating a course lesson for testing.

    Returns:
        CourseLesson: course lesson instance
    """
    return CourseLessonFactory.create()
