# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lessons serializers."""

import pytest

from apps.lessons.api.v1.serializers.lesson_detail_serializer import (
    LessonDetailSerializer,
)
from apps.lessons.api.v1.serializers.lessons_list_serializer import (
    LessonsListSerializer,
)
from apps.lessons.tests.factories import LessonFactory


@pytest.mark.django_db
def test_lessons_list_serializer() -> None:
    lesson = LessonFactory.create(
        title="Guitar Basics",
        description="Learn the basics",
    )

    data = LessonsListSerializer(lesson).data

    assert data["uuid"] == str(lesson.uuid)
    assert data["title"] == "Guitar Basics"
    assert data["description"] == "Learn the basics"
    assert data["songs"] == []


@pytest.mark.django_db
def test_lessons_list_serializer_with_songs() -> None:
    lesson = LessonFactory.create(title="Song Lesson", songs=2)

    data = LessonsListSerializer(lesson).data

    assert len(data["songs"]) == 2


@pytest.mark.django_db
def test_lesson_detail_serializer() -> None:
    lesson = LessonFactory.create(
        title="Advanced Guitar",
        description="Advanced techniques",
        video_url="https://example.com/video",
        duration=1800,
    )

    data = LessonDetailSerializer(lesson).data

    assert data["uuid"] == str(lesson.uuid)
    assert data["title"] == "Advanced Guitar"
    assert data["description"] == "Advanced techniques"
    assert data["video_url"] == "https://example.com/video"
    assert data["duration"] == 1800
    assert data["songs"] == []
    assert data["addition_lessons"] == []


@pytest.mark.django_db
def test_lesson_detail_serializer_with_songs() -> None:
    lesson = LessonFactory.create(songs=2)

    data = LessonDetailSerializer(lesson).data

    assert len(data["songs"]) == 2
    assert "chords" in data["songs"][0]
    assert "schemes" in data["songs"][0]


@pytest.mark.django_db
def test_lesson_detail_serializer_with_addition_lessons() -> None:
    additional = LessonFactory.create(
        title="Extra Lesson", video_url="https://example.com/extra"
    )
    lesson = LessonFactory.create(addition_lessons=[additional])

    data = LessonDetailSerializer(lesson).data

    assert len(data["addition_lessons"]) == 1
    assert data["addition_lessons"][0]["uuid"] == str(additional.uuid)
    assert data["addition_lessons"][0]["title"] == "Extra Lesson"
    assert data["addition_lessons"][0]["video_url"] == "https://example.com/extra"
