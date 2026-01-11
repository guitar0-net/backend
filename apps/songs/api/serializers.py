# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializers for the songs app."""

from rest_framework import serializers

from apps.chords.api.serializers import ChordOutputSerializer
from apps.schemes.api.serializers import ImageSchemeSerializer
from apps.songs.models import Song


class SongOutputSerializer(serializers.ModelSerializer[Song]):
    """Output song serializer."""

    chords = ChordOutputSerializer(many=True, read_only=True)
    schemes = ImageSchemeSerializer(many=True, read_only=True)

    class Meta:
        model = Song
        fields = ("id", "title", "text", "metronome", "schemes", "chords")
