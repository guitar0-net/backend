# SPDX-FileCopyrightText: 2025 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from apps.chords.models import Chord
from apps.chords.selectors import get_all_chords, get_chord_by_id
from apps.chords.tests.factories import FullChordFactory


@pytest.fixture
def multiple_chords_in_db(
    chord_factory: type[FullChordFactory],
) -> tuple[Chord, Chord, Chord]:
    c1 = chord_factory.create(
        title="F", musical_title="F major", order_in_note=1, has_barre=True
    )
    c2 = chord_factory.create(
        title="Am", musical_title="A minor", order_in_note=2, has_barre=False
    )
    c3 = chord_factory.create(
        title="Bm", musical_title="B minor", order_in_note=3, has_barre=True
    )
    return c1, c2, c3


@pytest.mark.django_db
def test_get_chord_by_id_success(chord_factory: type[FullChordFactory]) -> None:
    chord_instance = chord_factory.create(title="E7")

    retrieved_chord = get_chord_by_id(chord_instance.pk)

    assert retrieved_chord is not None
    assert retrieved_chord.title == "E7"
    assert retrieved_chord.pk == chord_instance.pk
    assert retrieved_chord.positions.count() == 6


@pytest.mark.django_db
def test_get_chord_by_id_not_found() -> None:
    non_existent_id = 999

    result = get_chord_by_id(non_existent_id)

    assert result is None


@pytest.mark.django_db
def test_get_chords_with_positions_returns_all_chords(
    multiple_chords_in_db: tuple[Chord, Chord, Chord],
) -> None:
    """Test that get_chords_with_positions returns all chords ordered correctly."""
    qs = get_all_chords()

    assert qs.count() == 3
    titles = [c.title for c in qs]
    assert titles == ["Am", "Bm", "F"]

    for chord in qs:
        assert chord.positions.count() == 6
