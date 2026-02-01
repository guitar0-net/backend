# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for courses API views."""

import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.courses.tests.factories import CourseFactory


@pytest.fixture
def api_client() -> APIClient:
    """Return API client."""
    return APIClient()


# =============================================================================
# CoursesListView tests
# =============================================================================


@pytest.mark.django_db
def test_courses_list_returns_published_courses(api_client: APIClient) -> None:
    """GET /courses/ returns list of published courses."""
    course = CourseFactory.create(title="Test Course")

    response = api_client.get(reverse("courses-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Test Course"
    assert response.data[0]["uuid"] == str(course.uuid)
    assert response.data[0]["lessons_count"] == 0


@pytest.mark.django_db
def test_courses_list_returns_empty_when_no_courses(api_client: APIClient) -> None:
    """GET /courses/ returns empty list when no courses exist."""
    response = api_client.get(reverse("courses-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_courses_list_excludes_unpublished(api_client: APIClient) -> None:
    """GET /courses/ excludes unpublished courses."""
    CourseFactory.create(title="Published", is_published=True)
    CourseFactory.create(title="Unpublished", is_published=False)

    response = api_client.get(reverse("courses-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Published"


# =============================================================================
# CourseDetailView tests
# =============================================================================


@pytest.mark.django_db
def test_course_detail_returns_course(api_client: APIClient) -> None:
    """GET /courses/{uuid}/ returns course details."""
    course = CourseFactory.create(title="Detail Test", description="Test description")

    response = api_client.get(reverse("course-detail", kwargs={"uuid": course.uuid}))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["uuid"] == str(course.uuid)
    assert response.data["title"] == "Detail Test"
    assert response.data["description"] == "Test description"


@pytest.mark.django_db
def test_course_detail_returns_404_for_nonexistent_uuid(
    api_client: APIClient,
) -> None:
    """GET /courses/{uuid}/ returns 404 for non-existent UUID."""
    nonexistent_uuid = uuid.uuid4()

    response = api_client.get(
        reverse("course-detail", kwargs={"uuid": nonexistent_uuid})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_course_detail_returns_404_for_unpublished(api_client: APIClient) -> None:
    """GET /courses/{uuid}/ returns 404 for unpublished course."""
    course = CourseFactory.create(is_published=False)

    response = api_client.get(reverse("course-detail", kwargs={"uuid": course.uuid}))

    assert response.status_code == status.HTTP_404_NOT_FOUND
