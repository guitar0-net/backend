# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for chord position."""

from rest_framework import serializers

from apps.chords.models import ChordPosition


class ChordPositionSerializer(serializers.ModelSerializer[ChordPosition]):
    """Serializer for one string position."""

    class Meta:
        model = ChordPosition
        fields = ("string_number", "fret", "finger")
