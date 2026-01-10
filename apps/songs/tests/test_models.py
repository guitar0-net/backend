# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for Song model."""

import pytest

from apps.chords.tests.factories import ChordFactory
from apps.schemes.tests.factories import ImageSchemeFactory
from apps.songs.models import Song
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_song_factory_creates_song(song_factory: SongFactory) -> None:
    song = song_factory.create()

    assert song.pk is not None
    assert song.title
    assert song.text
    assert 60 <= song.metronome <= 180


@pytest.mark.django_db
def test_song_str_method(song_factory: SongFactory) -> None:
    song = song_factory.create(title="Test Song")

    assert str(song) == "Test Song"


@pytest.mark.django_db
def test_song_with_chords_via_list(song_factory: SongFactory) -> None:
    chord1 = ChordFactory.create()
    chord2 = ChordFactory.create()

    song = song_factory.create(chords=[chord1, chord2])

    assert song.chords.count() == 2
    assert chord1 in song.chords.all()
    assert chord2 in song.chords.all()


@pytest.mark.django_db
def test_song_with_chords_via_count(song_factory: SongFactory) -> None:
    song = song_factory.create(chords=3)

    assert song.chords.count() == 3


@pytest.mark.django_db
def test_song_with_schemes_via_list(song_factory: SongFactory) -> None:
    scheme1 = ImageSchemeFactory.create()
    scheme2 = ImageSchemeFactory.create()

    song = song_factory.create(schemes=[scheme1, scheme2])

    assert song.schemes.count() == 2
    assert scheme1 in song.schemes.all()
    assert scheme2 in song.schemes.all()


@pytest.mark.django_db
def test_song_with_schemes_via_count(song_factory: SongFactory) -> None:
    song = song_factory.create(schemes=2)

    assert song.schemes.count() == 2


@pytest.mark.django_db
def test_song_without_chords_and_schemes(song_factory: SongFactory) -> None:
    song = song_factory.create()

    assert song.chords.count() == 0
    assert song.schemes.count() == 0


@pytest.mark.django_db
def test_song_metronome_default_value() -> None:
    song = Song.objects.create(
        title="Test Song",
        text="Test text",
    )

    assert song.metronome == 0


@pytest.mark.django_db
def test_song_title_max_length(song_factory: SongFactory) -> None:
    long_title = "A" * 200

    song = song_factory.create(title=long_title)

    assert len(song.title) == 200
    assert song.title == long_title


@pytest.mark.django_db
def test_song_get_or_create_by_title(song_factory: SongFactory) -> None:
    song1 = song_factory.create(title="Unique Song")
    song2 = song_factory.create(title="Unique Song")

    assert song1.pk == song2.pk
    assert Song.objects.filter(title="Unique Song").count() == 1
