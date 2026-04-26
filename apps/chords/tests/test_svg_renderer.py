# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the chord SVG renderer."""

import pytest

from apps.chords.models import Chord
from apps.chords.services import ChordCreateDict, ChordPositionCreateDict, ChordService
from apps.chords.svg_renderer import render_chord_svg

_DEFAULT_POSITIONS: list[ChordPositionCreateDict] = [
    {"string_number": 1, "fret": 1, "finger": 1},
    {"string_number": 2, "fret": 2, "finger": 2},
    {"string_number": 3, "fret": 2, "finger": 3},
    {"string_number": 4, "fret": 0, "finger": 0},
    {"string_number": 5, "fret": -1, "finger": 0},
    {"string_number": 6, "fret": -1, "finger": 0},
]


def _make_chord(
    title: str = "Am",
    has_barre: bool = False,
    start_fret: int = 1,
    positions: list[ChordPositionCreateDict] | None = None,
) -> Chord:
    chord_fields: ChordCreateDict = {
        "title": title,
        "musical_title": "A minor",
        "order_in_note": 1,
        "start_fret": start_fret,
        "has_barre": has_barre,
    }
    return ChordService.create_chord(
        positions=positions or _DEFAULT_POSITIONS,
        chord_fields=chord_fields,
    )


@pytest.mark.django_db
def test_render_chord_svg_returns_two_strings() -> None:
    chord = _make_chord()

    horizontal, _vertical = render_chord_svg(chord)

    assert isinstance(horizontal, str)


@pytest.mark.django_db
def test_render_chord_svg_vertical_returns_string() -> None:
    chord = _make_chord()

    _, vertical = render_chord_svg(chord)

    assert isinstance(vertical, str)


@pytest.mark.django_db
def test_horizontal_svg_contains_viewbox() -> None:
    chord = _make_chord()

    horizontal, _ = render_chord_svg(chord)

    assert "viewBox" in horizontal


@pytest.mark.django_db
def test_vertical_svg_contains_viewbox() -> None:
    chord = _make_chord()

    _, vertical = render_chord_svg(chord)

    assert "viewBox" in vertical


@pytest.mark.django_db
def test_muted_string_produces_cross_marker() -> None:
    chord = _make_chord(
        positions=[
            {"string_number": 1, "fret": -1, "finger": 0},
            {"string_number": 2, "fret": 1, "finger": 1},
            {"string_number": 3, "fret": 1, "finger": 2},
            {"string_number": 4, "fret": 1, "finger": 3},
            {"string_number": 5, "fret": 1, "finger": 4},
            {"string_number": 6, "fret": 1, "finger": 0},
        ]
    )

    horizontal, _ = render_chord_svg(chord)

    assert "×" in horizontal


@pytest.mark.django_db
def test_open_string_produces_circle_marker() -> None:
    chord = _make_chord(
        positions=[
            {"string_number": 1, "fret": 0, "finger": 0},
            {"string_number": 2, "fret": 1, "finger": 1},
            {"string_number": 3, "fret": 1, "finger": 2},
            {"string_number": 4, "fret": 1, "finger": 3},
            {"string_number": 5, "fret": 1, "finger": 4},
            {"string_number": 6, "fret": 1, "finger": 0},
        ]
    )

    horizontal, _ = render_chord_svg(chord)

    assert "○" in horizontal


@pytest.mark.django_db
def test_pressed_string_produces_circle_element() -> None:
    chord = _make_chord(
        positions=[
            {"string_number": 1, "fret": 2, "finger": 1},
            {"string_number": 2, "fret": 2, "finger": 2},
            {"string_number": 3, "fret": 2, "finger": 3},
            {"string_number": 4, "fret": 2, "finger": 4},
            {"string_number": 5, "fret": -1, "finger": 0},
            {"string_number": 6, "fret": -1, "finger": 0},
        ]
    )

    horizontal, _ = render_chord_svg(chord)

    assert "<circle" in horizontal


@pytest.mark.django_db
def test_finger_number_appears_in_svg() -> None:
    chord = _make_chord(
        positions=[
            {"string_number": 1, "fret": 2, "finger": 3},
            {"string_number": 2, "fret": 2, "finger": 2},
            {"string_number": 3, "fret": 2, "finger": 1},
            {"string_number": 4, "fret": -1, "finger": 0},
            {"string_number": 5, "fret": -1, "finger": 0},
            {"string_number": 6, "fret": -1, "finger": 0},
        ]
    )

    horizontal, _ = render_chord_svg(chord)

    assert ">3<" in horizontal


@pytest.mark.django_db
def test_barre_chord_produces_ellipse_element() -> None:
    chord = _make_chord(
        has_barre=True,
        positions=[
            {"string_number": 1, "fret": 2, "finger": 1},
            {"string_number": 2, "fret": 2, "finger": 1},
            {"string_number": 3, "fret": 2, "finger": 1},
            {"string_number": 4, "fret": 2, "finger": 1},
            {"string_number": 5, "fret": 2, "finger": 1},
            {"string_number": 6, "fret": 2, "finger": 1},
        ],
    )

    horizontal, _ = render_chord_svg(chord)

    assert "<ellipse" in horizontal


@pytest.mark.django_db
def test_aria_label_present_on_svg_element() -> None:
    chord = _make_chord()

    horizontal, _ = render_chord_svg(chord)

    assert 'aria-label="' in horizontal


@pytest.mark.django_db
def test_aria_label_is_non_empty() -> None:
    chord = _make_chord(title="Em")

    horizontal, _ = render_chord_svg(chord)

    assert 'aria-label=""' not in horizontal


@pytest.mark.django_db
def test_aria_label_escapes_special_characters() -> None:
    chord = _make_chord(title='A"m')

    horizontal, _ = render_chord_svg(chord)

    assert 'aria-label="A&quot;m' in horizontal


# Horizontal layout constants: ml=15, mt=22, string_h=12
# tonic marker y = mt + (_STRINGS - tonic_string) * string_h + 3
# tonic marker x = ml - 5 = 10
@pytest.mark.django_db
@pytest.mark.parametrize(
    ("title", "expected_y"),
    [
        ("G", 25),  # tonic_string=6 → tonic_sy=22 → y=25
        ("Em", 25),  # tonic_string=6 → tonic_sy=22 → y=25
        ("Dm", 49),  # tonic_string=4 → tonic_sy=46 → y=49
        ("Cm", 37),  # tonic_string=5 → tonic_sy=34 → y=37
    ],
)
def test_tonic_marker_is_on_correct_string(title: str, expected_y: int) -> None:
    chord = _make_chord(title=title)

    horizontal, _ = render_chord_svg(chord)

    assert (
        f'x="10" y="{expected_y}" text-anchor="end" font-size="7" font-weight="bold"'
        in horizontal
    )
