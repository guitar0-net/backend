# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""PDF renderer for song print view."""

from typing import Literal, TypedDict

from django.template.loader import render_to_string
from markdownx.utils import markdownify  # type: ignore[import-untyped]
from weasyprint import HTML  # type: ignore[import-untyped]

from apps.songs.models import Song

type Size = Literal[1, 2, 3, 4, 5]
type Orientation = Literal["vertical", "horizontal"]


class PrintSettings(TypedDict):
    """Validated print settings passed from the request serializer."""

    show_chords: bool
    show_schemes: bool
    show_text: bool
    chord_orientation: Orientation
    chord_size: Size
    scheme_size: Size
    text_size: Size
    columns_count: int


_CHORD_WIDTHS: dict[Orientation, dict[Size, str]] = {
    "vertical": {
        1: "7rem",
        2: "8rem",
        3: "9rem",
        4: "10rem",
        5: "12rem",
    },
    "horizontal": {
        1: "12rem",
        2: "17rem",
        3: "22rem",
        4: "26rem",
        5: "32rem",
    },
}

_SCHEME_WIDTHS: dict[Size, str] = {
    1: "100px",
    2: "140px",
    3: "180px",
    4: "220px",
    5: "260px",
}

_FONT_SIZES: dict[Size, str] = {
    1: "9pt",
    2: "10pt",
    3: "11pt",
    4: "13pt",
    5: "15pt",
}


def render_song_pdf(song: Song, settings: PrintSettings) -> bytes:
    """Render a Song to PDF bytes applying the given print settings."""
    chords = []
    if settings["show_chords"]:
        for chord in song.chords.all():
            svg = (
                chord.svg_vertical
                if settings["chord_orientation"] == "vertical"
                else chord.svg_horizontal
            )
            if svg:
                chords.append({"title": chord.title, "svg": svg})

    schemes = []
    if settings["show_schemes"]:
        for scheme in song.schemes.all():
            if scheme.image:
                schemes.append({
                    "path": f"file://{scheme.image.path}",
                    "inscription": scheme.inscription,
                })

    text_html = ""
    if settings["show_text"] and song.text:
        text_html = markdownify(song.text)

    context = {
        "song_title": song.title,
        "chords": chords,
        "schemes": schemes,
        "text_html": text_html,
        "columns_count": settings["columns_count"],
        "chord_width": _CHORD_WIDTHS[settings["chord_orientation"]][
            settings["chord_size"]
        ],
        "scheme_width": _SCHEME_WIDTHS[settings["scheme_size"]],
        "text_font_size": _FONT_SIZES[settings["text_size"]],
    }

    html_string = render_to_string("songs/song_print.html", context)
    return HTML(string=html_string).write_pdf()  # type: ignore[no-any-return]
