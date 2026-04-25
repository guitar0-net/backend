# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lessons API views."""

import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.courses.tests.factories import CourseFactory
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
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Test Lesson"
    assert response.data["results"][0]["uuid"] == str(lesson.uuid)


@pytest.mark.django_db
def test_lessons_list_returns_empty_when_no_lessons(api_client: APIClient) -> None:
    """GET /lessons/ returns empty list when no lessons exist."""
    response = api_client.get(reverse("lessons-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


@pytest.mark.django_db
def test_lessons_list_excludes_unpublished(api_client: APIClient) -> None:
    """GET /lessons/ excludes unpublished lessons."""
    LessonFactory.create(title="Published", is_published=True)
    LessonFactory.create(title="Unpublished", is_published=False)

    response = api_client.get(reverse("lessons-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Published"


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


@pytest.mark.django_db
def test_lesson_detail_course_is_null_when_course_is_unpublished(
    api_client: APIClient,
) -> None:
    lesson = LessonFactory.create()
    course = CourseFactory.create(lessons=[lesson], is_published=False)

    url = reverse("lesson-detail", kwargs={"uuid": lesson.uuid})
    response = api_client.get(url, {"course": str(course.uuid)})

    assert response.data["course"] is None


@pytest.mark.django_db
def test_lesson_detail_course_is_null_when_course_param_is_malformed(
    api_client: APIClient,
) -> None:
    lesson = LessonFactory.create()

    url = reverse("lesson-detail", kwargs={"uuid": lesson.uuid})
    response = api_client.get(url, {"course": "не-uuid"})

    assert response.data["course"] is None


@pytest.mark.django_db
def test_lesson_detail_course_is_null_when_course_uuid_not_in_lesson(
    api_client: APIClient,
) -> None:
    lesson = LessonFactory.create()
    unrelated_course = CourseFactory.create()

    url = reverse("lesson-detail", kwargs={"uuid": lesson.uuid})
    response = api_client.get(url, {"course": str(unrelated_course.uuid)})

    assert response.data["course"] is None


@pytest.mark.django_db
def test_lesson_detail_course_is_null_when_no_course_param(
    api_client: APIClient,
) -> None:
    lesson = LessonFactory.create()

    response = api_client.get(reverse("lesson-detail", kwargs={"uuid": lesson.uuid}))

    assert response.data["course"] is None


@pytest.mark.django_db
def test_lesson_detail_course_contains_uuid_and_title_when_valid_course_param(
    api_client: APIClient,
) -> None:
    lesson = LessonFactory.create()
    course = CourseFactory.create(title="Джаз для гитаристов", lessons=[lesson])

    url = reverse("lesson-detail", kwargs={"uuid": lesson.uuid})
    response = api_client.get(url, {"course": str(course.uuid)})

    expected = {"uuid": str(course.uuid), "title": "Джаз для гитаристов"}
    assert response.data["course"] == expected
