# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for song print settings."""

from rest_framework import serializers

from apps.songs.constants import ChordOrientationChoice, SizeChoice


class SongPrintSettingsSerializer(serializers.Serializer[None]):
    """Deserialize and validate PDF print settings from the request body."""

    show_chords = serializers.BooleanField(default=True)
    show_schemes = serializers.BooleanField(default=True)
    show_text = serializers.BooleanField(default=True)
    chord_orientation = serializers.ChoiceField(
        choices=ChordOrientationChoice.choices,
        default=ChordOrientationChoice.VERTICAL,
    )
    chord_size = serializers.ChoiceField(
        choices=SizeChoice.choices,
        default=SizeChoice.MD,
    )
    scheme_size = serializers.ChoiceField(
        choices=SizeChoice.choices,
        default=SizeChoice.MD,
    )
    text_size = serializers.ChoiceField(
        choices=SizeChoice.choices,
        default=SizeChoice.MD,
    )
    columns_count = serializers.IntegerField(
        min_value=1,
        max_value=3,
        default=1,
    )
