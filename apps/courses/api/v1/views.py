# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the courses app."""

import logging

from django.db.models import QuerySet
from django.http import Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.courses.models import Course
from apps.courses.selectors import get_course_by_uuid, get_published_courses

from .serializers.course_detail_serializer import CourseDetailSerializer
from .serializers.courses_list_serializer import CoursesListSerializer

logger = logging.getLogger("courses")


class CoursesListView(ListAPIView[Course]):
    """List all published courses."""

    permission_classes = (AllowAny,)
    serializer_class = CoursesListSerializer

    def get_queryset(self) -> QuerySet[Course]:  # noqa: PLR6301
        """Return published courses queryset."""
        logger.debug("Fetching published courses list")
        return get_published_courses()


class CourseDetailView(RetrieveAPIView[Course]):
    """Retrieve a single published course by UUID."""

    permission_classes = (AllowAny,)
    serializer_class = CourseDetailSerializer

    def get_object(self) -> Course:
        """Return course by UUID or raise 404."""
        uuid = self.kwargs["uuid"]
        course = get_course_by_uuid(uuid)
        if course is None:
            logger.warning("Course not found: uuid=%s", uuid)
            raise Http404
        logger.debug("Fetched course: uuid=%s, title=%s", uuid, course.title)
        return course
