# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for Lesson model."""

import uuid

import pytest

from apps.lessons.models import Lesson
from apps.lessons.tests.factories import LessonFactory
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_lesson_factory_creates_lesson() -> None:
    lesson = LessonFactory.create()

    assert lesson.pk is not None
    assert lesson.title
    assert lesson.uuid
    assert 30 <= lesson.duration <= 3600
    assert lesson.video_url


@pytest.mark.django_db
def test_lesson_uuid_is_auto_generated() -> None:
    lesson = LessonFactory.create()

    assert isinstance(lesson.uuid, uuid.UUID)


@pytest.mark.django_db
def test_lesson_uuid_is_unique() -> None:
    lesson1 = LessonFactory.create()
    lesson2 = LessonFactory.create()

    assert lesson1.uuid != lesson2.uuid


@pytest.mark.django_db
def test_lesson_str_method() -> None:
    lesson = LessonFactory.create(title="Introduction")

    assert str(lesson) == "Lesson: 'Introduction'"


@pytest.mark.django_db
def test_lesson_default_fields() -> None:
    lesson = Lesson()

    assert lesson.is_published is True


@pytest.mark.django_db
def test_lesson_with_songs_via_list() -> None:
    song1 = SongFactory.create()
    song2 = SongFactory.create()

    lesson = LessonFactory.create(songs=[song1, song2])

    assert lesson.songs.count() == 2
    assert song1 in lesson.songs.all()
    assert song2 in lesson.songs.all()


@pytest.mark.django_db
def test_lesson_with_songs_via_count() -> None:
    lesson = LessonFactory.create(songs=3)

    assert lesson.songs.count() == 3


@pytest.mark.django_db
def test_lesson_without_songs() -> None:
    lesson = LessonFactory.create()

    assert lesson.songs.count() == 0


@pytest.mark.django_db
def test_lesson_with_addition_lessons_via_list() -> None:
    extra1 = LessonFactory.create()
    extra2 = LessonFactory.create()

    lesson = LessonFactory.create(addition_lessons=[extra1, extra2])

    assert lesson.addition_lessons.count() == 2
    assert extra1 in lesson.addition_lessons.all()
    assert extra2 in lesson.addition_lessons.all()


@pytest.mark.django_db
def test_lesson_with_addition_lessons_via_count() -> None:
    lesson = LessonFactory.create(addition_lessons=2)

    assert lesson.addition_lessons.count() == 2


@pytest.mark.django_db
def test_lesson_addition_lessons_asymmetric() -> None:
    lesson1 = LessonFactory.create()
    lesson2 = LessonFactory.create(addition_lessons=[lesson1])

    assert lesson1 in lesson2.addition_lessons.all()
    assert lesson2 not in lesson1.addition_lessons.all()


@pytest.mark.django_db
def test_lesson_recommended_for_reverse_relation() -> None:
    lesson1 = LessonFactory.create()
    lesson2 = LessonFactory.create(addition_lessons=[lesson1])

    assert lesson2 in lesson1.recommended_for.all()


@pytest.mark.django_db
def test_lesson_blank_description() -> None:
    lesson = LessonFactory.create(description="")

    assert not lesson.description


@pytest.mark.django_db
def test_lesson_title_max_length() -> None:
    long_title = "A" * 200

    lesson = LessonFactory.create(title=long_title)

    assert len(lesson.title) == 200
    assert lesson.title == long_title


@pytest.mark.django_db
def test_lesson_is_published_default() -> None:
    lesson = Lesson.objects.create(
        title="Test",
        video_url="https://example.com/video",
    )

    assert lesson.is_published is True


@pytest.mark.django_db
def test_lesson_songs_related_name() -> None:
    song = SongFactory.create()
    lesson = LessonFactory.create(songs=[song])

    assert lesson in song.lessons.all()
