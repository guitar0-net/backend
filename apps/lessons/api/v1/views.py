# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the lessons app."""

import logging

from django.db.models import QuerySet
from django.http import Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.lessons.models import Lesson
from apps.lessons.selectors import get_lesson_by_uuid, get_published_lessons

from .serializers.lesson_detail_serializer import LessonDetailSerializer
from .serializers.lessons_list_serializer import LessonsListSerializer

logger = logging.getLogger("lessons")


class LessonsListView(ListAPIView[Lesson]):
    """List all published lessons."""

    permission_classes = (AllowAny,)
    serializer_class = LessonsListSerializer

    def get_queryset(self) -> QuerySet[Lesson]:  # noqa: PLR6301
        """Return published lessons queryset."""
        logger.debug("Fetching published lessons list")
        return get_published_lessons()


class LessonDetailView(RetrieveAPIView[Lesson]):
    """Retrieve a single published lesson by UUID."""

    permission_classes = (AllowAny,)
    serializer_class = LessonDetailSerializer

    def get_object(self) -> Lesson:
        """Return lesson by UUID or raise 404."""
        uuid = self.kwargs["uuid"]
        lesson = get_lesson_by_uuid(uuid)
        if lesson is None:
            logger.warning("Lesson not found: uuid=%s", uuid)
            raise Http404
        logger.debug("Fetched lesson: uuid=%s, title=%s", uuid, lesson.title)
        return lesson
