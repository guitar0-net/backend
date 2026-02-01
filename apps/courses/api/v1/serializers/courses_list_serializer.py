# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the courses list."""

from rest_framework import serializers

from apps.courses.models import Course


class CoursesListSerializer(serializers.ModelSerializer[Course]):
    """Serializer for courses list."""

    lessons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ("uuid", "title", "description", "lessons_count")
