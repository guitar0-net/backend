# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures for testing the reports app."""

import uuid
from pathlib import Path

import pytest
from faker import Faker
from pytest_django.fixtures import Settings
from rest_framework.test import APIClient

from apps.reports.constants import ClientPlatform, ReportReason, ReportTargetType
from apps.reports.services import ReportSubmission
from apps.reports.throttling import ReportDeviceRateThrottle


@pytest.fixture
def api_client() -> APIClient:
    """Return an unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def media_root(settings: Settings, tmp_path: Path) -> Path:
    """Point MEDIA_ROOT at a temporary directory for uploaded scheme images."""
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


@pytest.fixture
def fake() -> Faker:
    """Return a Faker producing Cyrillic text."""
    return Faker("ru_RU")


@pytest.fixture
def app_submission(fake: Faker) -> ReportSubmission:
    """Return a valid, random bug report about the app itself."""
    return ReportSubmission(
        id=uuid.uuid4(),
        target_type=ReportTargetType.APP,
        target_id="",
        reason=ReportReason.BUG,
        message=fake.sentence(),
        contact_email=fake.email(),
        device_id=str(uuid.uuid4()),
        platform=ClientPlatform.IOS,
        app_version=fake.numerify("#.#.#"),
        os_version=fake.numerify("##.#"),
        locale=fake.locale(),
        screen=fake.word(),
    )


@pytest.fixture
def device_rate_limit() -> int:
    """Return how many reports one device may send per period."""
    throttle = ReportDeviceRateThrottle()
    allowed, _duration = throttle.parse_rate(throttle.get_rate())
    if allowed is None:
        pytest.fail("the report device scope has no configured rate")
    return allowed
