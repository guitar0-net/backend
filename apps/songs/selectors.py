# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the songs app."""

import uuid as uuid_module
from collections.abc import Iterable

from django.db.models import QuerySet

from apps.songs.models import Song


def get_song_by_uuid(uuid: uuid_module.UUID) -> Song | None:
    """Return a Song by UUID with prefetched chords and schemes, or None."""
    return Song.objects.filter(uuid=uuid).prefetch_related("chords", "schemes").first()


def get_songs_by_uuids_for_update(uuids: Iterable[uuid_module.UUID]) -> QuerySet[Song]:
    """Return the songs with these UUIDs, row-locked, with prefetched chords.

    The lock keeps an admin edit from slipping between reading a song's text
    and writing a value derived from it; evaluate inside a transaction.
    """
    return (
        Song.objects
        .select_for_update()
        .filter(uuid__in=list(uuids))
        .prefetch_related("chords")
    )
