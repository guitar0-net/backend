# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for lesson detail."""

from rest_framework import serializers

from apps.lessons.api.v1.serializers.lessons_list_serializer import (
    LessonsListSerializer,
)
from apps.lessons.models import Lesson
from apps.songs.api.v1.serializers.song_detail_serializer import SongDetailSerializer


class LessonDetailSerializer(serializers.ModelSerializer[Lesson]):
    """Serializer for lesson detail."""

    songs = SongDetailSerializer(many=True, read_only=True)
    addition_lessons = LessonsListSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "uuid",
            "title",
            "description",
            "video_url",
            "duration",
            "songs",
            "addition_lessons",
        )
