# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the chords list."""

from rest_framework import serializers

from apps.chords.models import Chord

from .chord_position_serializer import ChordPositionSerializer


class ChordsListSerializer(serializers.ModelSerializer[Chord]):
    """Serializer for chords list."""

    positions = ChordPositionSerializer(many=True, read_only=True)

    class Meta:
        model = Chord
        fields = ("id", "title", "musical_title", "positions")
