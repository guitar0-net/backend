# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the announcements app."""

import logging

from django.db.models import QuerySet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.announcements.models import Announcement
from apps.announcements.selectors import get_published_announcements

from .serializers.announcement_detail_serializer import AnnouncementDetailSerializer
from .serializers.announcements_list_serializer import AnnouncementsListSerializer

logger = logging.getLogger("announcements")


class AnnouncementsListView(ListAPIView[Announcement]):
    """List all published announcements."""

    permission_classes = (AllowAny,)
    serializer_class = AnnouncementsListSerializer

    def get_queryset(self) -> QuerySet[Announcement]:  # noqa: PLR6301
        """Return published announcements queryset."""
        logger.debug("Fetching published announcements list")
        return get_published_announcements()


class AnnouncementDetailView(RetrieveAPIView[Announcement]):
    """Retrieve a single published announcement by UUID."""

    permission_classes = (AllowAny,)
    serializer_class = AnnouncementDetailSerializer
    lookup_field = "uuid"

    def get_queryset(self) -> QuerySet[Announcement]:  # noqa: PLR6301
        """Return the published announcement queryset."""
        return get_published_announcements()
