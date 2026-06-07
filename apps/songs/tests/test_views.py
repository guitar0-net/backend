# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs API views."""

import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.songs.tests.factories import SongFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_returns_pdf_content_type(api_client: APIClient) -> None:
    song = SongFactory.create(title="Тест Ñoño")

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}), data={}, format="json"
    )

    assert response["Content-Type"] == "application/pdf"


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_returns_200_with_empty_body(api_client: APIClient) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}), data={}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_response_content_is_valid_pdf(api_client: APIClient) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}), data={}, format="json"
    )

    assert response.content[:4] == b"%PDF"


@pytest.mark.django_db
def test_song_print_returns_404_for_nonexistent_uuid(api_client: APIClient) -> None:
    response = api_client.post(
        reverse("song-print", kwargs={"uuid": uuid.uuid4()}),
        data={},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_song_print_returns_400_for_invalid_columns_count(
    api_client: APIClient,
) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}),
        data={"columns_count": 10},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_song_print_returns_400_for_invalid_chord_size(api_client: APIClient) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}),
        data={"chord_size": 6},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_content_disposition_is_inline(api_client: APIClient) -> None:
    song = SongFactory.create(title="Звёздочка")

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}), data={}, format="json"
    )

    assert response["Content-Disposition"] == 'inline; filename="Zvyozdochka.pdf"'


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_accepts_all_size_choices(api_client: APIClient) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}),
        data={"chord_size": 5, "scheme_size": 1, "text_size": 4},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_with_show_chords_false_returns_pdf(api_client: APIClient) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}),
        data={"show_chords": False, "show_schemes": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.django_db
def test_song_print_with_three_columns_returns_pdf(api_client: APIClient) -> None:
    song = SongFactory.create()

    response = api_client.post(
        reverse("song-print", kwargs={"uuid": song.uuid}),
        data={"columns_count": 3},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
