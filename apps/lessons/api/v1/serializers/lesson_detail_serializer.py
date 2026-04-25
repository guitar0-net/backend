# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for lesson detail."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.lessons.api.v1.serializers.lessons_list_serializer import (
    LessonsListSerializer,
)
from apps.lessons.models import Lesson
from apps.songs.api.v1.serializers.song_detail_serializer import SongDetailSerializer

_COURSE_SCHEMA = {
    "type": "object",
    "nullable": True,
    "properties": {
        "uuid": {"type": "string", "format": "uuid"},
        "title": {"type": "string"},
    },
}


class LessonDetailSerializer(serializers.ModelSerializer[Lesson]):
    """Serializer for lesson detail."""

    songs = SongDetailSerializer(many=True, read_only=True)
    addition_lessons = LessonsListSerializer(many=True, read_only=True)
    course = serializers.SerializerMethodField()

    @extend_schema_field(_COURSE_SCHEMA)
    def get_course(self, _obj: Lesson) -> dict[str, str] | None:
        """Return course context for breadcrumb rendering, or None."""
        course = self.context.get("course")
        if course is None:
            return None
        return {"uuid": str(course.uuid), "title": course.title}

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
            "course",
        )
