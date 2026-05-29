# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializers for the sync endpoint — flat/normalized format."""

from typing import Any

from rest_framework import serializers

from apps.chords.models import Chord
from apps.courses.models import Course, CourseLesson
from apps.lessons.models import Lesson
from apps.schemes.models import ImageScheme


class LessonFlatSerializer(serializers.ModelSerializer[Lesson]):
    """Lesson fields only — songs are in the top-level songs array."""

    class Meta:
        model = Lesson
        fields = ("uuid", "updated_at", "title", "description", "video_url", "duration")


class SongFlatSerializer(serializers.Serializer[Any]):
    """Song with chord_ids/scheme_ids instead of nested objects."""

    uuid = serializers.UUIDField()
    lesson_uuid = serializers.UUIDField()
    title = serializers.CharField()
    text = serializers.CharField()
    metronome = serializers.IntegerField()
    chord_ids = serializers.ListField(child=serializers.IntegerField())
    scheme_ids = serializers.ListField(child=serializers.IntegerField())


class ChordSyncSerializer(serializers.ModelSerializer[Chord]):
    """Chord for offline sync."""

    class Meta:
        model = Chord
        fields = (
            "id",
            "title",
            "musical_title",
            "order_in_note",
            "start_fret",
            "has_barre",
            "svg_horizontal",
            "svg_vertical",
        )


class SchemeSyncSerializer(serializers.ModelSerializer[ImageScheme]):
    """Scheme for offline sync — id and image URL only."""

    class Meta:
        model = ImageScheme
        fields = ("id", "image")


class CourseFlatSerializer(serializers.ModelSerializer[Course]):
    """Course fields only — memberships are in the top-level course_lessons array."""

    class Meta:
        model = Course
        fields = ("uuid", "title", "description", "created_at", "updated_at")


class CourseLessonFlatSerializer(serializers.ModelSerializer[CourseLesson]):
    """Course-lesson membership with both UUIDs explicit."""

    course_uuid = serializers.UUIDField(source="course.uuid")
    lesson_uuid = serializers.UUIDField(source="lesson.uuid")

    class Meta:
        model = CourseLesson
        fields = ("course_uuid", "lesson_uuid", "order")
