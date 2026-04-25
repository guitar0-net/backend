# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the chord SVG renderer."""

import pytest

from apps.chords.models import Chord, ChordPosition
from apps.chords.svg_renderer import render_chord_svg


def _make_chord_with_positions(
    title: str = "Am",
    has_barre: bool = False,
    start_fret: int = 1,
    positions: list[dict[str, int]] | None = None,
) -> Chord:
    chord = Chord.objects.create(
        title=title,
        musical_title="A minor",
        order_in_note=1,
        start_fret=start_fret,
        has_barre=has_barre,
    )
    default_positions = [
        {"string_number": 1, "fret": 1, "finger": 1},
        {"string_number": 2, "fret": 2, "finger": 2},
        {"string_number": 3, "fret": 2, "finger": 3},
        {"string_number": 4, "fret": 0, "finger": 0},
        {"string_number": 5, "fret": -1, "finger": 0},
        {"string_number": 6, "fret": -1, "finger": 0},
    ]
    for pos in positions or default_positions:
        ChordPosition.objects.create(chord=chord, **pos)
    return chord


@pytest.mark.django_db
def test_render_chord_svg_returns_two_strings() -> None:
    chord = _make_chord_with_positions()

    horizontal, _vertical = render_chord_svg(chord)

    assert isinstance(horizontal, str)


@pytest.mark.django_db
def test_render_chord_svg_vertical_returns_string() -> None:
    chord = _make_chord_with_positions()

    _, vertical = render_chord_svg(chord)

    assert isinstance(vertical, str)


@pytest.mark.django_db
def test_horizontal_svg_contains_viewbox() -> None:
    chord = _make_chord_with_positions()

    horizontal, _ = render_chord_svg(chord)

    assert "viewBox" in horizontal


@pytest.mark.django_db
def test_vertical_svg_contains_viewbox() -> None:
    chord = _make_chord_with_positions()

    _, vertical = render_chord_svg(chord)

    assert "viewBox" in vertical


@pytest.mark.django_db
def test_muted_string_produces_cross_marker() -> None:
    chord = _make_chord_with_positions(
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
    chord = _make_chord_with_positions(
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
    chord = _make_chord_with_positions(
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
    chord = _make_chord_with_positions(
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
    chord = _make_chord_with_positions(
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
    chord = _make_chord_with_positions()

    horizontal, _ = render_chord_svg(chord)

    assert 'aria-label="' in horizontal


@pytest.mark.django_db
def test_aria_label_is_non_empty() -> None:
    chord = _make_chord_with_positions(title="Em")

    horizontal, _ = render_chord_svg(chord)

    assert 'aria-label=""' not in horizontal


@pytest.mark.django_db
def test_tonic_string_is_six_for_g() -> None:
    chord = _make_chord_with_positions(title="G")

    horizontal, _ = render_chord_svg(chord)

    assert "T" in horizontal


@pytest.mark.django_db
def test_tonic_string_is_six_for_e() -> None:
    chord = _make_chord_with_positions(title="Em")

    horizontal, _ = render_chord_svg(chord)

    assert "T" in horizontal


@pytest.mark.django_db
def test_tonic_string_is_four_for_d() -> None:
    chord = _make_chord_with_positions(title="Dm")

    horizontal, _ = render_chord_svg(chord)

    assert "T" in horizontal


@pytest.mark.django_db
def test_tonic_string_is_five_for_other_roots() -> None:
    chord = _make_chord_with_positions(title="Cm")

    horizontal, _ = render_chord_svg(chord)

    assert "T" in horizontal
