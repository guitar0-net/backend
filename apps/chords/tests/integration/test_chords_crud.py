# SPDX-FileCopyrightText: 2025-2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Integration tests for chords app."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.chords.models import Chord
from apps.chords.tests.factories import FullChordFactory


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.integration
@pytest.mark.django_db
def test_chords_list_and_retrieve_flow(
    client: APIClient,
    chord_factory: type[FullChordFactory],
) -> None:
    chord: Chord = chord_factory.create(
        title="Am",
        musical_title="A minor",
        order_in_note=1,
        start_fret=1,
        has_barre=False,
    )

    list_response = client.get("/api/v1/data/chords/")

    assert list_response.status_code == status.HTTP_200_OK
    assert any(c["id"] == chord.pk for c in list_response.json())

    retrieve_response = client.get(f"/api/v1/data/chords/{chord.pk}/")

    assert retrieve_response.status_code == status.HTTP_200_OK
    data = retrieve_response.json()
    assert data["id"] == chord.pk
    assert data["title"] == "Am"
    assert data["musical_title"] == "A minor"
    assert len(data["positions"]) == 6


@pytest.mark.integration
@pytest.mark.django_db
def test_chords_retrieve_not_found(client: APIClient) -> None:
    response = client.get("/api/v1/data/chords/99999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
