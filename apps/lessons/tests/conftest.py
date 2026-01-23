# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures for testing lessons app."""

import pytest

from apps.lessons.models import Lesson
from apps.lessons.tests.factories import LessonFactory


@pytest.fixture
def lesson() -> Lesson:
    """Fixture creating a lesson for testing.

    Returns:
        Lesson: lesson instance
    """
    return LessonFactory.create()
