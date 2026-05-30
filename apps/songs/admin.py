# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin settings for songs."""

from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin  # type: ignore[import-untyped]

from apps.songs.models import Song
from apps.songs.services import save_song


@admin.register(Song)
class SongAdmin(MarkdownxModelAdmin):  # type: ignore[misc]
    """Admin interface for the Song model."""

    filter_horizontal = ("chords", "schemes")
    list_display = ("title", "metronome")
    list_editable = ("metronome",)

    def save_model(  # noqa: PLR6301
        self,
        request: object,
        obj: Song,
        form: object,
        change: object,
    ) -> None:
        """Save the song and propagate the change timestamp to related lessons."""
        save_song(obj)
