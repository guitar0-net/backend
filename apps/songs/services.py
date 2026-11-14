# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Services for the songs app."""

import hashlib
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.lessons.services import touch_lessons_for_songs
from apps.songs.chord_text import find_chord_text_errors, find_unknown_chords
from apps.songs.models import Song
from apps.songs.selectors import get_songs_by_uuids


@dataclass(frozen=True)
class ChordTextImport:
    """A converted `chord_text` and the hex SHA-256 of the text it came from."""

    song_uuid: uuid.UUID
    source_sha256: str
    chord_text: str


@dataclass
class ChordTextImportReport:
    """What `import_chord_texts` did, or would do on a dry run, with each song."""

    updated: list[uuid.UUID] = field(default_factory=list)
    stale: list[uuid.UUID] = field(default_factory=list)
    unknown: list[uuid.UUID] = field(default_factory=list)
    already_filled: list[uuid.UUID] = field(default_factory=list)
    invalid: dict[uuid.UUID, list[str]] = field(default_factory=dict)
    unknown_chords: dict[uuid.UUID, set[str]] = field(default_factory=dict)


@transaction.atomic
def save_song(song: Song) -> None:
    """Persist a Song instance and propagate the change to related lessons.

    All Song mutations must go through this function — calling song.save()
    directly bypasses the propagation and leaves Lesson.updated_at stale.

    Propagation updates `updated_at` on every Lesson that uses this song so
    that the sync endpoint reflects content changes originating in a song.
    """
    song.save()
    touch_lessons_for_songs([song.pk])


@transaction.atomic
def delete_song(song: Song) -> None:
    """Delete a Song instance, propagating to related lessons first.

    The lesson-to-song rows that identify the affected lessons are removed
    along with the song, so they must be read before the delete.
    """
    if song.pk is not None:
        touch_lessons_for_songs([song.pk])
        song.delete()


@transaction.atomic
def delete_songs(songs: QuerySet[Song]) -> None:
    """Delete every song in the queryset, propagating to related lessons.

    Serves the admin bulk action, which never routes through `delete_song`.
    """
    touch_lessons_for_songs(list(songs.values_list("pk", flat=True)))
    songs.delete()


@transaction.atomic
def import_chord_texts(
    imports: Sequence[ChordTextImport],
    *,
    overwrite: bool,
    dry_run: bool,
) -> ChordTextImportReport:
    """Fill `Song.chord_text` from conversions made outside the backend.

    A conversion is skipped when the song's current `text` no longer hashes
    to `source_sha256` (edited after the snapshot), when its markup is
    malformed, and — unless `overwrite` — when the song already has a
    `chord_text`, which may hold edits made in admin. Chord names missing
    from the song's chords are only reported.

    The bulk update bypasses `save_song`, so lessons are touched here, once
    for all updated songs, and `updated_at` is set by hand because
    `bulk_update` skips `auto_now`. A dry run reads without locking rows.
    """
    report = ChordTextImportReport()
    songs = {
        song.uuid: song
        for song in get_songs_by_uuids(
            (item.song_uuid for item in imports), for_update=not dry_run
        )
    }
    now = timezone.now()
    changed: list[Song] = []
    for item in imports:
        song = songs.get(item.song_uuid)
        if song is None:
            report.unknown.append(item.song_uuid)
        elif (
            hashlib.sha256(song.text.encode()).hexdigest() != item.source_sha256.lower()
        ):
            report.stale.append(song.uuid)
        elif song.chord_text and not overwrite:
            report.already_filled.append(song.uuid)
        elif errors := find_chord_text_errors(item.chord_text):
            report.invalid[song.uuid] = errors
        else:
            unknown_chords = find_unknown_chords(
                item.chord_text, (chord.title for chord in song.chords.all())
            )
            if unknown_chords:
                report.unknown_chords[song.uuid] = unknown_chords
            song.chord_text = item.chord_text
            song.updated_at = now
            changed.append(song)
            report.updated.append(song.uuid)

    if changed and not dry_run:
        Song.objects.bulk_update(changed, ["chord_text", "updated_at"])
        touch_lessons_for_songs([song.pk for song in changed])
    return report
