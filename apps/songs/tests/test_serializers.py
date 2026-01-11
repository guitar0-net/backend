# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from apps.chords.tests.factories import ChordFactory
from apps.schemes.tests.factories import ImageSchemeFactory
from apps.songs.api.serializers import SongOutputSerializer
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_output_data() -> None:
    schemes = ImageSchemeFactory.create_batch(
        2,
        height=100,
        width=200,
    )
    chords = ChordFactory.create_batch(1)

    song = SongFactory.create(
        title="Song 1",
        text="song text",
        metronome=80,
        chords=chords,
        schemes=schemes,
    )

    data = SongOutputSerializer(song).data

    assert data["id"] == song.pk
    assert data["title"] == "Song 1"
    assert data["text"] == "song text"
    assert data["metronome"] == 80

    assert len(data["schemes"]) == 2
    assert {s["pk"] for s in data["schemes"]} == {s.pk for s in schemes}

    assert len(data["chords"]) == 1
    chord_data = data["chords"][0]
    assert chord_data["id"] == chords[0].id
    assert chord_data["title"] == chords[0].title
