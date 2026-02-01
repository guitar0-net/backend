# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for chord detail."""

from rest_framework import serializers

from apps.chords.models import Chord

from .chord_position_serializer import ChordPositionSerializer


class ChordDetailSerializer(serializers.ModelSerializer[Chord]):
    """Serializer for chord detail."""

    positions = ChordPositionSerializer(many=True, read_only=True)

    class Meta:
        model = Chord
        fields = (
            "id",
            "title",
            "musical_title",
            "order_in_note",
            "start_fret",
            "has_barre",
            "positions",
        )
