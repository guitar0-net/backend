# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for list of songs."""

from rest_framework import serializers

from apps.songs.models import Song


class SongListSerializer(serializers.ModelSerializer[Song]):
    """Serializer for list of songs."""

    class Meta:
        model = Song
        fields = ("id", "title")
