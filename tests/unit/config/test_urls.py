# SPDX-FileCopyrightText: 2025 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.test import Client
from django.urls import resolve, reverse
from pytest_django.fixtures import SettingsWrapper
from rest_framework import status

from apps.accounts.models.user import User


@pytest.mark.parametrize(
    "url_name",
    [
        "admin:index",
    ],
)
def test_url_resolves(url_name: str) -> None:
    url = reverse(url_name)
    resolved = resolve(url)
    assert resolved.view_name == url_name


@pytest.mark.django_db
def test_markdownx_markdownify_turns_an_anonymous_caller_away() -> None:
    response = Client().post(
        reverse("markdownx_markdownify"), data={"content": "мягкий знак"}
    )

    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_markdownx_markdownify_renders_for_staff(
    staff_user: User,
    settings: SettingsWrapper,
) -> None:
    settings.MARKDOWNX_MARKDOWN_EXTENSIONS = []
    client = Client()
    client.force_login(staff_user)

    response = client.post(
        reverse("markdownx_markdownify"), data={"content": "**жирный**"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_markdownx_markdownify_turns_a_signed_in_non_staff_caller_away(
    common_user: User,
) -> None:
    client = Client()
    client.force_login(common_user)

    response = client.post(
        reverse("markdownx_markdownify"), data={"content": "щи да борщ"}
    )

    assert response.status_code == status.HTTP_302_FOUND


def test_the_markdown_editor_points_at_the_markdownify_route(
    settings: SettingsWrapper,
) -> None:
    resolved = resolve(str(settings.MARKDOWNX_URLS_PATH))

    assert resolved.view_name == "markdownx_markdownify"
