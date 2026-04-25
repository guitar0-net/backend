# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the chords API views."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.chords.services import ChordCreateDict, ChordPositionCreateDict, ChordService
from apps.chords.tests.factories import FullChordFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def _full_positions() -> list[ChordPositionCreateDict]:
    return [
        {"string_number": 1, "fret": 1, "finger": 1},
        {"string_number": 2, "fret": 2, "finger": 2},
        {"string_number": 3, "fret": 2, "finger": 3},
        {"string_number": 4, "fret": 0, "finger": 0},
        {"string_number": 5, "fret": -1, "finger": 0},
        {"string_number": 6, "fret": -1, "finger": 0},
    ]


@pytest.mark.django_db
def test_chords_list_includes_svg_horizontal(api_client: APIClient) -> None:
    fields: ChordCreateDict = {
        "title": "Dm",
        "musical_title": "D minor",
        "order_in_note": 1,
        "start_fret": 1,
        "has_barre": False,
    }
    ChordService.create_chord(positions=_full_positions(), chord_fields=fields)

    response = api_client.get("/api/v1/chords/")

    assert "svg_horizontal" in response.json()["results"][0]


@pytest.mark.django_db
def test_chords_list_includes_svg_vertical(api_client: APIClient) -> None:
    fields: ChordCreateDict = {
        "title": "Dm",
        "musical_title": "D minor",
        "order_in_note": 1,
        "start_fret": 1,
        "has_barre": False,
    }
    ChordService.create_chord(positions=_full_positions(), chord_fields=fields)

    response = api_client.get("/api/v1/chords/")

    assert "svg_vertical" in response.json()["results"][0]


@pytest.mark.django_db
def test_chord_detail_includes_svg_horizontal(
    api_client: APIClient,
    chord_factory: type[FullChordFactory],
) -> None:
    chord = chord_factory.create(
        title="Em",
        musical_title="E minor",
        order_in_note=1,
        start_fret=1,
        has_barre=False,
    )

    response = api_client.get(f"/api/v1/chords/{chord.pk}/")

    assert "svg_horizontal" in response.json()


@pytest.mark.django_db
def test_chord_detail_includes_svg_vertical(
    api_client: APIClient,
    chord_factory: type[FullChordFactory],
) -> None:
    chord = chord_factory.create(
        title="Em",
        musical_title="E minor",
        order_in_note=1,
        start_fret=1,
        has_barre=False,
    )

    response = api_client.get(f"/api/v1/chords/{chord.pk}/")

    assert "svg_vertical" in response.json()


@pytest.mark.django_db
def test_chords_list_returns_200(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/chords/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_chord_detail_returns_200(
    api_client: APIClient,
    chord_factory: type[FullChordFactory],
) -> None:
    chord = chord_factory.create()

    response = api_client.get(f"/api/v1/chords/{chord.pk}/")

    assert response.status_code == status.HTTP_200_OK
