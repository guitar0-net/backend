# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lessons API views."""

import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.lessons.tests.factories import LessonFactory


@pytest.fixture
def api_client() -> APIClient:
    """Return API client."""
    return APIClient()


# =============================================================================
# LessonsListView tests
# =============================================================================


@pytest.mark.django_db
def test_lessons_list_returns_published_lessons(api_client: APIClient) -> None:
    """GET /lessons/ returns list of published lessons."""
    lesson = LessonFactory.create(title="Test Lesson")

    response = api_client.get(reverse("lessons-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Test Lesson"
    assert response.data[0]["uuid"] == str(lesson.uuid)


@pytest.mark.django_db
def test_lessons_list_returns_empty_when_no_lessons(api_client: APIClient) -> None:
    """GET /lessons/ returns empty list when no lessons exist."""
    response = api_client.get(reverse("lessons-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_lessons_list_excludes_unpublished(api_client: APIClient) -> None:
    """GET /lessons/ excludes unpublished lessons."""
    LessonFactory.create(title="Published", is_published=True)
    LessonFactory.create(title="Unpublished", is_published=False)

    response = api_client.get(reverse("lessons-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Published"


# =============================================================================
# LessonDetailView tests
# =============================================================================


@pytest.mark.django_db
def test_lesson_detail_returns_lesson(api_client: APIClient) -> None:
    """GET /lessons/{uuid}/ returns lesson details."""
    lesson = LessonFactory.create(title="Detail Test", description="Test description")

    response = api_client.get(reverse("lesson-detail", kwargs={"uuid": lesson.uuid}))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["uuid"] == str(lesson.uuid)
    assert response.data["title"] == "Detail Test"
    assert response.data["description"] == "Test description"


@pytest.mark.django_db
def test_lesson_detail_returns_404_for_nonexistent_uuid(
    api_client: APIClient,
) -> None:
    """GET /lessons/{uuid}/ returns 404 for non-existent UUID."""
    nonexistent_uuid = uuid.uuid4()

    response = api_client.get(
        reverse("lesson-detail", kwargs={"uuid": nonexistent_uuid})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_lesson_detail_returns_404_for_unpublished(api_client: APIClient) -> None:
    """GET /lessons/{uuid}/ returns 404 for unpublished lesson."""
    lesson = LessonFactory.create(is_published=False)

    response = api_client.get(reverse("lesson-detail", kwargs={"uuid": lesson.uuid}))

    assert response.status_code == status.HTTP_404_NOT_FOUND
