# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for announcements API views."""

import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.announcements.tests.factories import AnnouncementFactory


@pytest.fixture
def api_client() -> APIClient:
    """Return API client."""
    return APIClient()


# =============================================================================
# AnnouncementsListView tests
# =============================================================================


@pytest.mark.django_db
def test_announcements_list_returns_published(api_client: APIClient) -> None:
    """GET /announcements/ returns list of published announcements."""
    announcement = AnnouncementFactory.create(
        title="Test Announcement", published_at=timezone.now() - timedelta(minutes=1)
    )

    response = api_client.get(reverse("announcements-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Test Announcement"
    assert response.data[0]["uuid"] == str(announcement.uuid)


@pytest.mark.django_db
def test_announcements_list_returns_empty_when_none(api_client: APIClient) -> None:
    """GET /announcements/ returns empty list when no announcements exist."""
    response = api_client.get(reverse("announcements-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_announcements_list_excludes_unpublished(api_client: APIClient) -> None:
    """GET /announcements/ excludes unpublished announcements."""
    now = timezone.now()
    # Published
    AnnouncementFactory.create(title="Published", published_at=now - timedelta(days=1))
    # Scheduled for future
    AnnouncementFactory.create(title="Future", published_at=now + timedelta(days=1))
    # Draft
    AnnouncementFactory.create(title="Draft", published_at=None)

    response = api_client.get(reverse("announcements-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Published"


# =============================================================================
# AnnouncementDetailView tests
# =============================================================================


@pytest.mark.django_db
def test_announcement_detail_returns_announcement(api_client: APIClient) -> None:
    """GET /announcements/{uuid}/ returns announcement details."""
    announcement = AnnouncementFactory.create(
        title="Detail Test",
        content="Some content",
        published_at=timezone.now() - timedelta(minutes=1),
    )

    response = api_client.get(
        reverse("announcement-detail", kwargs={"uuid": announcement.uuid})
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["uuid"] == str(announcement.uuid)
    assert response.data["title"] == "Detail Test"
    assert response.data["content"] == "Some content"


@pytest.mark.django_db
def test_announcement_detail_returns_404_for_nonexistent_uuid(
    api_client: APIClient,
) -> None:
    """GET /announcements/{uuid}/ returns 404 for non-existent UUID."""
    nonexistent_uuid = uuid.uuid4()

    response = api_client.get(
        reverse("announcement-detail", kwargs={"uuid": nonexistent_uuid})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_announcement_detail_returns_404_for_unpublished(
    api_client: APIClient,
) -> None:
    """GET /announcements/{uuid}/ returns 404 for unpublished announcement."""
    # Scheduled for future
    a1 = AnnouncementFactory.create(published_at=timezone.now() + timedelta(days=1))

    response = api_client.get(reverse("announcement-detail", kwargs={"uuid": a1.uuid}))

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Draft
    a2 = AnnouncementFactory.create(published_at=None)

    response = api_client.get(reverse("announcement-detail", kwargs={"uuid": a2.uuid}))

    assert response.status_code == status.HTTP_404_NOT_FOUND
