# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin settings for songs."""

from django.contrib import admin

from apps.songs.models import Song


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Admin interface for the Song model."""

    filter_horizontal = ("chords", "schemes")
    list_display = ("title", "metronome")
    list_editable = ("metronome",)
