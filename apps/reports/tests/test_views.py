# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports API views."""

import string
import uuid

import pytest
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.accounts.tests.factories.user import UserFactory
from apps.chords.tests.factories import ChordFactory
from apps.reports.constants import (
    REPORT_CREATE_THROTTLE_SCOPE,
    ClientPlatform,
    ReportReason,
    ReportTargetType,
)
from apps.reports.selectors import get_report_by_id
from apps.songs.tests.factories import SongFactory


@pytest.fixture
def payload(fake: Faker) -> dict[str, str]:
    """Return a valid, random request body reporting a bug in the app."""
    return {
        "id": str(uuid.uuid4()),
        "target_type": ReportTargetType.APP,
        "reason": ReportReason.BUG,
        "message": fake.sentence(),
        "device_id": str(uuid.uuid4()),
        "platform": ClientPlatform.ANDROID,
        "app_version": fake.numerify("#.#.#"),
    }


@pytest.fixture
def create_rate_limit() -> int:
    """Return how many reports the configured scope allows per period."""
    throttle = ScopedRateThrottle()
    throttle.scope = REPORT_CREATE_THROTTLE_SCOPE
    allowed, _duration = throttle.parse_rate(throttle.get_rate())
    if allowed is None:
        pytest.fail("the report_create scope has no configured rate")
    return allowed


@pytest.mark.django_db
def test_report_create_answers_created_for_a_new_report(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    response = api_client.post(reverse("report-create"), payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_report_create_answers_ok_for_a_resubmitted_report(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    api_client.post(reverse("report-create"), payload, format="json")

    response = api_client.post(reverse("report-create"), payload, format="json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_report_create_does_not_echo_the_submitted_message(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    response = api_client.post(reverse("report-create"), payload, format="json")

    assert set(response.data) == {"id", "status", "created_at"}


@pytest.mark.django_db
def test_report_create_records_the_signed_in_user(
    api_client: APIClient, payload: dict[str, str], fake: Faker
) -> None:
    user = UserFactory.create(email=fake.email())
    api_client.force_authenticate(user)

    api_client.post(reverse("report-create"), payload, format="json")

    report = get_report_by_id(uuid.UUID(payload["id"]))
    assert report is not None and report.user == user


@pytest.mark.django_db
def test_report_create_accepts_a_report_about_an_existing_song(
    api_client: APIClient, payload: dict[str, str], fake: Faker
) -> None:
    song = SongFactory.create(title=fake.sentence())
    body = {
        **payload,
        "target_type": ReportTargetType.SONG,
        "target_id": str(song.uuid),
        "reason": ReportReason.WRONG_LYRICS,
    }

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_report_create_rejects_a_song_that_does_not_exist(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    body = {
        **payload,
        "target_type": ReportTargetType.SONG,
        "target_id": str(uuid.uuid4()),
        "reason": ReportReason.WRONG_CHORDS,
    }

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_stores_an_uppercase_song_uuid_in_canonical_form(
    api_client: APIClient, payload: dict[str, str], fake: Faker
) -> None:
    song = SongFactory.create(title=fake.sentence())
    body = {
        **payload,
        "target_type": ReportTargetType.SONG,
        "target_id": str(song.uuid).upper(),
        "reason": ReportReason.WRONG_LYRICS,
    }

    api_client.post(reverse("report-create"), body, format="json")

    report = get_report_by_id(uuid.UUID(payload["id"]))
    assert report is not None and report.target_id == str(song.uuid)


@pytest.mark.django_db
def test_report_create_stores_a_chord_id_in_ascii_digits(
    api_client: APIClient, payload: dict[str, str], fake: Faker
) -> None:
    chord = ChordFactory.create(title=fake.lexify("??"))
    arabic_indic = str.maketrans(string.digits, "٠١٢٣٤٥٦٧٨٩")
    body = {
        **payload,
        "target_type": ReportTargetType.CHORD,
        "target_id": f"0{chord.pk}".translate(arabic_indic),
        "reason": ReportReason.WRONG_FINGERING,
    }

    api_client.post(reverse("report-create"), body, format="json")

    report = get_report_by_id(uuid.UUID(payload["id"]))
    assert report is not None and report.target_id == str(chord.pk)


@pytest.mark.django_db
def test_report_create_rejects_a_song_id_that_is_not_a_uuid(
    api_client: APIClient, payload: dict[str, str], fake: Faker
) -> None:
    body = {
        **payload,
        "target_type": ReportTargetType.SONG,
        "target_id": fake.word(),
        "reason": ReportReason.WRONG_CHORDS,
    }

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_rejects_a_chord_id_that_is_not_an_integer(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    body = {
        **payload,
        "target_type": ReportTargetType.CHORD,
        "target_id": str(uuid.uuid4()),
        "reason": ReportReason.WRONG_FINGERING,
    }

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_rejects_a_reason_not_offered_for_the_target_type(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    body = {**payload, "reason": ReportReason.WRONG_CHORDS}

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_rejects_a_target_id_for_the_app_itself(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    body = {**payload, "target_id": str(uuid.uuid4())}

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_requires_a_target_id_for_a_song(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    body = {
        **payload,
        "target_type": ReportTargetType.SONG,
        "reason": ReportReason.WRONG_LYRICS,
    }

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_requires_a_message_for_a_feature_request(
    api_client: APIClient, payload: dict[str, str]
) -> None:
    body = {**payload, "reason": ReportReason.FEATURE_REQUEST, "message": "  "}

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_rejects_a_malformed_contact_email(
    api_client: APIClient, payload: dict[str, str], fake: Faker
) -> None:
    body = {**payload, "contact_email": fake.word()}

    response = api_client.post(reverse("report-create"), body, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_report_create_throttles_a_flood_from_one_client(
    api_client: APIClient, payload: dict[str, str], create_rate_limit: int
) -> None:
    for _ in range(create_rate_limit):
        api_client.post(
            reverse("report-create"),
            {**payload, "id": str(uuid.uuid4())},
            format="json",
        )

    response = api_client.post(reverse("report-create"), payload, format="json")

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_report_reasons_lists_every_target_type(api_client: APIClient) -> None:
    response = api_client.get(reverse("report-reasons"))

    assert {entry["target_type"] for entry in response.data} == set(
        ReportTargetType.values
    )


def test_report_reasons_flags_feature_requests_as_needing_a_message(
    api_client: APIClient,
) -> None:
    response = api_client.get(reverse("report-reasons"))

    app_reasons = next(
        entry["reasons"]
        for entry in response.data
        if entry["target_type"] == ReportTargetType.APP
    )
    assert next(
        reason["requires_message"]
        for reason in app_reasons
        if reason["code"] == ReportReason.FEATURE_REQUEST
    )
