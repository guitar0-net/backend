# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the announcements app."""

from django.db.models import QuerySet
from django.utils import timezone

from apps.announcements.models import Announcement


def get_published_announcements() -> QuerySet[Announcement]:
    """Get a QuerySet of all published Announcement objects.

    Returns:
        QuerySet[Announcement]: Published announcements ordered by creation date.
    """
    return Announcement.objects.filter(
        published_at__isnull=False, published_at__lte=timezone.now()
    ).order_by("-published_at")
