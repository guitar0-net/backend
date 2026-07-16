# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for accounts API views."""

from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.factories.user import UserFactory


@pytest.fixture
def api_client() -> APIClient:
    """Return API client."""
    return APIClient()


def _stub_claims(
    monkeypatch: pytest.MonkeyPatch,
    *,
    sub: str = "246810",
    email: str = "олег@example.com",
) -> None:
    monkeypatch.setattr(
        "apps.accounts.services.verify_google_id_token",
        lambda id_token: {
            "sub": sub,
            "email": email,
            "email_verified": True,
            "given_name": "Олег",
            "family_name": "Петров",
            "picture": "https://example.com/avatar/oleg.jpg",
        },
    )


@pytest.mark.django_db
def test_google_auth_returns_access_and_refresh_tokens(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_claims(monkeypatch)

    response = api_client.post(
        reverse("auth-google"), {"id_token": "stub-token"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_google_auth_returns_user_profile_from_google_claims(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_claims(monkeypatch)

    response = api_client.post(
        reverse("auth-google"), {"id_token": "stub-token"}, format="json"
    )

    assert response.data["user"] == {
        "email": "олег@example.com",
        "display_name": "Олег Петров",
        "avatar": "https://example.com/avatar/oleg.jpg",
    }


@pytest.mark.django_db
def test_google_auth_returns_same_user_on_repeated_request(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_claims(monkeypatch)
    first = api_client.post(
        reverse("auth-google"), {"id_token": "stub-token"}, format="json"
    )

    second = api_client.post(
        reverse("auth-google"), {"id_token": "stub-token"}, format="json"
    )

    assert second.data["user"]["email"] == first.data["user"]["email"]


@pytest.mark.django_db
def test_google_auth_returns_400_for_invalid_token(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise(*_args: object, **_kwargs: object) -> None:
        raise ValueError("Wrong number of segments in token")

    monkeypatch.setattr(
        "apps.accounts.services.google_id_token.verify_oauth2_token", _raise
    )

    response = api_client.post(
        reverse("auth-google"), {"id_token": "not-a-real-token"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_token_refresh_returns_new_access_token_for_valid_refresh_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="ирина@example.com")
    refresh = RefreshToken.for_user(user)

    response = api_client.post(
        reverse("token-refresh"), {"refresh": str(refresh)}, format="json"
    )

    assert "access" in response.data


@pytest.mark.django_db
def test_token_refresh_returns_a_different_refresh_token_due_to_rotation(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="жанна@example.com")
    old_refresh = str(RefreshToken.for_user(user))

    response = api_client.post(
        reverse("token-refresh"), {"refresh": old_refresh}, format="json"
    )

    assert response.data["refresh"] != old_refresh


@pytest.mark.django_db
def test_token_refresh_rejects_reused_refresh_token_after_rotation(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="святослав@example.com")
    old_refresh = str(RefreshToken.for_user(user))
    api_client.post(reverse("token-refresh"), {"refresh": old_refresh}, format="json")

    response = api_client.post(
        reverse("token-refresh"), {"refresh": old_refresh}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_refresh_returns_401_for_an_invalid_refresh_token(
    api_client: APIClient,
) -> None:
    response = api_client.post(
        reverse("token-refresh"), {"refresh": "not-a-real-token"}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_verify_returns_200_for_a_valid_access_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="тарас@example.com")
    access = str(RefreshToken.for_user(user).access_token)

    response = api_client.post(
        reverse("token-verify"), {"token": access}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_token_verify_returns_401_for_an_expired_access_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="богдана@example.com")
    access = RefreshToken.for_user(user).access_token
    access.set_exp(lifetime=timedelta(seconds=-1))

    response = api_client.post(
        reverse("token-verify"), {"token": str(access)}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_verify_returns_401_for_a_malformed_token(
    api_client: APIClient,
) -> None:
    response = api_client.post(
        reverse("token-verify"), {"token": "не-настоящий-токен"}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
