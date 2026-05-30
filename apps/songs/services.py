# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Services for the songs app."""

from django.utils import timezone

from apps.songs.models import Song


def save_song(song: Song) -> None:
    """Persist a Song instance and propagate the change to related lessons.

    All Song mutations must go through this function — calling song.save()
    directly bypasses the propagation and leaves Lesson.updated_at stale.

    Propagation updates `updated_at` on every Lesson that uses this song so
    that the sync endpoint reflects content changes originating in a song.
    Uses queryset.update() to avoid N+1 saves and to bypass auto_now
    restrictions on Lesson.updated_at.
    """
    song.save()
    song.lessons.all().update(updated_at=timezone.now())
