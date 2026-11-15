# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports throttling."""

import uuid

import pytest
from faker import Faker
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.reports.throttling import ReportDeviceRateThrottle


def _request(body: object, ip: str) -> Request:
    return Request(
        APIRequestFactory().post("/", body, format="json", REMOTE_ADDR=ip),
        parsers=[JSONParser()],
    )


def _exhaust(body: object, ip: str, times: int) -> None:
    for _ in range(times):
        ReportDeviceRateThrottle().allow_request(_request(body, ip), APIView())


@pytest.fixture
def ip(fake: Faker) -> str:
    """Return a random client IP address."""
    return fake.ipv4()


def test_device_throttle_rejects_a_device_past_its_quota(
    ip: str, device_rate_limit: int
) -> None:
    body = {"device_id": f"устройство-{uuid.uuid4()}"}
    _exhaust(body, ip, device_rate_limit)

    allowed = ReportDeviceRateThrottle().allow_request(_request(body, ip), APIView())

    assert allowed is False


def test_device_throttle_admits_another_device_behind_the_same_ip(
    ip: str, device_rate_limit: int
) -> None:
    _exhaust({"device_id": f"устройство-{uuid.uuid4()}"}, ip, device_rate_limit)

    allowed = ReportDeviceRateThrottle().allow_request(
        _request({"device_id": f"устройство-{uuid.uuid4()}"}, ip), APIView()
    )

    assert allowed is True


def test_device_throttle_limits_by_ip_when_the_device_id_is_missing(
    ip: str, device_rate_limit: int
) -> None:
    _exhaust({"message": "без устройства"}, ip, device_rate_limit)

    allowed = ReportDeviceRateThrottle().allow_request(
        _request({"message": "снова без устройства"}, ip), APIView()
    )

    assert allowed is False


def test_device_throttle_limits_by_ip_when_the_body_is_not_an_object(
    ip: str, device_rate_limit: int
) -> None:
    _exhaust(["список", "вместо", "объекта"], ip, device_rate_limit)

    allowed = ReportDeviceRateThrottle().allow_request(
        _request(["снова", "список"], ip), APIView()
    )

    assert allowed is False
