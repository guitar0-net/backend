# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for chords management commands."""

import pytest
from django.core.management import call_command

from apps.chords.models import Chord
from apps.chords.tests.factories import FullChordFactory


@pytest.mark.django_db
def test_generate_chord_svgs_populates_svg_fields(
    chord_factory: type[FullChordFactory],
) -> None:
    chord = chord_factory.create(
        title="Am",
        musical_title="A minor",
        order_in_note=1,
        start_fret=1,
        has_barre=False,
    )
    Chord.objects.filter(pk=chord.pk).update(svg_horizontal="", svg_vertical="")

    call_command("generate_chord_svgs")

    chord.refresh_from_db()
    assert chord.svg_horizontal
    assert chord.svg_vertical
