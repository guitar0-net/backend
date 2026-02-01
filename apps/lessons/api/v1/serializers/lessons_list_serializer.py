# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the lessons list."""

from rest_framework import serializers

from apps.lessons.models import Lesson
from apps.songs.api.v1.serializers.songs_list_serializer import SongListSerializer


class LessonsListSerializer(serializers.ModelSerializer[Lesson]):
    """Serializer for lessons list."""

    songs = SongListSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ("uuid", "title", "description", "video_url", "songs")
