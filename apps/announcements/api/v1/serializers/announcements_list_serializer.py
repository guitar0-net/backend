# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the announcements list."""

from rest_framework import serializers

from apps.announcements.models import Announcement


class AnnouncementsListSerializer(serializers.ModelSerializer[Announcement]):
    """Serializer for announcements list."""

    class Meta:
        model = Announcement
        fields = ("uuid", "title", "slug", "product_version", "published_at")
