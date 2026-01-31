# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for course detail."""

from rest_framework import serializers

from apps.courses.models import Course, CourseLesson
from apps.lessons.api.v1.serializers.lessons_list_serializer import (
    LessonsListSerializer,
)


class CourseLessonDetailSerializer(serializers.Serializer[CourseLesson]):
    """Serializer for lesson within course detail."""

    order = serializers.IntegerField()
    lesson = LessonsListSerializer()


class CourseDetailSerializer(serializers.ModelSerializer[Course]):
    """Serializer for course detail."""

    lessons = CourseLessonDetailSerializer(source="course_lessons", many=True)

    class Meta:
        model = Course
        fields = ("uuid", "title", "description", "created_at", "updated_at", "lessons")
