# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for announcement detail."""

from rest_framework import serializers

from apps.announcements.models import Announcement


class AnnouncementDetailSerializer(serializers.ModelSerializer[Announcement]):
    """Serializer for announcement detail."""

    class Meta:
        model = Announcement
        fields = (
            "uuid",
            "title",
            "slug",
            "content",
            "product_version",
            "created_at",
            "updated_at",
        )
