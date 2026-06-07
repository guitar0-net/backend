# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs PDF renderer."""

from typing import Any, cast

import pytest

from apps.songs.pdf_renderer import PrintSettings, render_song_pdf
from apps.songs.tests.factories import SongFactory


def _default_settings(**overrides: Any) -> PrintSettings:  # noqa: ANN401
    base: dict[str, Any] = {
        "show_chords": True,
        "show_schemes": True,
        "show_text": True,
        "chord_orientation": "vertical",
        "chord_size": 3,
        "scheme_size": 3,
        "text_size": 3,
        "columns_count": 1,
    }
    return cast(PrintSettings, {**base, **overrides})


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_returns_bytes() -> None:
    song = SongFactory.create(text="Lyrics line одна")
    result = render_song_pdf(song, _default_settings())
    assert isinstance(result, bytes)


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_output_is_valid_pdf() -> None:
    song = SongFactory.create(text="Текст с аккордами [Am] тест")
    result = render_song_pdf(song, _default_settings())
    assert result[:4] == b"%PDF"


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_with_show_text_false_returns_pdf() -> None:
    song = SongFactory.create()
    result = render_song_pdf(song, _default_settings(show_text=False))
    assert result[:4] == b"%PDF"


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_with_show_chords_false_returns_pdf() -> None:
    song = SongFactory.create(chords=1)
    result = render_song_pdf(song, _default_settings(show_chords=False))
    assert result[:4] == b"%PDF"


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_with_horizontal_orientation_returns_pdf() -> None:
    song = SongFactory.create()
    result = render_song_pdf(song, _default_settings(chord_orientation="horizontal"))
    assert result[:4] == b"%PDF"


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_with_three_columns_returns_pdf() -> None:
    song = SongFactory.create(text="Куплет первый\n\nКуплет второй\n\nКуплет третий")
    result = render_song_pdf(song, _default_settings(columns_count=3))
    assert result[:4] == b"%PDF"


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_with_xl_sizes_returns_pdf() -> None:
    song = SongFactory.create()
    result = render_song_pdf(
        song,
        _default_settings(chord_size=5, scheme_size=5, text_size=5),
    )
    assert result[:4] == b"%PDF"


@pytest.mark.integration
@pytest.mark.django_db
def test_render_song_pdf_with_xs_sizes_returns_pdf() -> None:
    song = SongFactory.create()
    result = render_song_pdf(
        song,
        _default_settings(chord_size=1, scheme_size=1, text_size=1),
    )
    assert result[:4] == b"%PDF"
