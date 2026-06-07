# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the songs app."""

import uuid as uuid_module

from apps.songs.models import Song


def get_song_by_uuid(uuid: uuid_module.UUID) -> Song | None:
    """Return a Song by UUID with prefetched chords and schemes, or None."""
    return Song.objects.filter(uuid=uuid).prefetch_related("chords", "schemes").first()
