# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Integration tests for the ops application."""

from random import randint
from secrets import token_hex

import pytest
from django.test import Client


@pytest.mark.integration
@pytest.mark.django_db
def test_full_metrics_flow(client: Client) -> None:
    """Test that making requests results in metrics being recorded."""
    client.get("/api/v1/data/chords/")
    client.get("/api/v1/data/chords/")
    client.get("/admin/")

    response = client.get("/metrics/")
    content = response.content.decode("utf-8")

    assert "guitar0_backend_http_requests_total" in content
    assert "guitar0_backend_http_request_duration_seconds" in content
    assert "guitar0_backend_http_requests_in_progress" in content
    assert "guitar0_backend_http_exceptions_total" in content
    assert "guitar0_backend_app_info" in content


@pytest.mark.integration
@pytest.mark.django_db
def test_metrics_endpoint_not_counted(client: Client) -> None:
    """Verify that /metrics/ requests are not counted in metrics."""
    client.get("/metrics/")

    for _ in range(5):
        client.get("/metrics/")

    response = client.get("/metrics/")
    final_content = response.content.decode("utf-8")

    assert 'endpoint="/metrics/"' not in final_content


@pytest.mark.integration
@pytest.mark.django_db
def test_metrics_label_requests_by_route(client: Client) -> None:
    """Requests to one route share a label whatever the ID in the path."""
    client.get(f"/api/v1/chords/{randint(1, 10**9)}/")

    content = client.get("/metrics/").content.decode("utf-8")

    assert 'endpoint="/api/v1/chords/<int:pk>/"' in content


@pytest.mark.integration
@pytest.mark.django_db
def test_metrics_label_requests_by_unknown_path_as_unmatched(client: Client) -> None:
    """A path no route serves shares one label instead of naming the path."""
    method = f"PROBE{token_hex(4).upper()}"
    client.generic(method, f"/wp-includes/{token_hex(6)}-скан.php")

    content = client.get("/metrics/").content.decode("utf-8")

    assert f'endpoint="<unmatched>",method="{method}"' in content


@pytest.mark.integration
@pytest.mark.django_db
def test_app_info_metric_set_on_startup(client: Client) -> None:
    """Test that app_info metric is set when the app starts."""
    response = client.get("/metrics/")
    content = response.content.decode("utf-8")

    assert "guitar0_backend_app_info" in content
    assert "version=" in content
    assert "git_sha=" in content
    assert "build_datetime=" in content
