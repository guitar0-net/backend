# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs selectors."""

import uuid

import pytest

from apps.songs.selectors import get_song_by_uuid, get_songs_by_uuids_for_update
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_get_song_by_uuid_returns_song_when_uuid_matches() -> None:
    song = SongFactory.create()
    assert get_song_by_uuid(song.uuid) == song


@pytest.mark.django_db
def test_get_song_by_uuid_returns_none_when_uuid_does_not_match() -> None:
    assert get_song_by_uuid(uuid.uuid4()) is None


@pytest.mark.django_db
def test_get_song_by_uuid_prefetches_chords() -> None:
    song = SongFactory.create(chords=2)
    result = get_song_by_uuid(song.uuid)
    assert result is not None
    assert result.chords.all().count() == 2


@pytest.mark.django_db
def test_get_song_by_uuid_prefetches_schemes() -> None:
    song = SongFactory.create(schemes=1)
    result = get_song_by_uuid(song.uuid)
    assert result is not None
    assert result.schemes.all().count() == 1


@pytest.mark.django_db
def test_get_songs_by_uuids_for_update_returns_only_requested_songs() -> None:
    wanted = SongFactory.create(title="Кукушка")
    SongFactory.create(title="Спокойная ночь")

    assert list(get_songs_by_uuids_for_update([wanted.uuid, uuid.uuid4()])) == [wanted]
