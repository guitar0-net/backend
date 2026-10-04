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
    email: str = "user@example.com",
) -> None:
    monkeypatch.setattr(
        "apps.accounts.services.verify_google_id_token",
        lambda id_token: {
            "sub": sub,
            "email": email,
            "email_verified": True,
            "given_name": "Имя",
            "family_name": "Фамилия",
            "picture": "https://example.com/avatar/user.jpg",
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
        "email": "user@example.com",
        "display_name": "Имя Фамилия",
        "avatar": "https://example.com/avatar/user.jpg",
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
def test_google_auth_returns_403_when_the_email_belongs_to_a_staff_user(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    UserFactory.create(email="сотрудник@example.com", is_staff=True)
    _stub_claims(monkeypatch, email="сотрудник@example.com")

    response = api_client.post(
        reverse("auth-google"), {"id_token": "stub-token"}, format="json"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_token_refresh_returns_new_access_token_for_valid_refresh_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
    refresh = RefreshToken.for_user(user)

    response = api_client.post(
        reverse("token-refresh"), {"refresh": str(refresh)}, format="json"
    )

    assert "access" in response.data


@pytest.mark.django_db
def test_token_refresh_returns_a_different_refresh_token_due_to_rotation(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
    old_refresh = str(RefreshToken.for_user(user))

    response = api_client.post(
        reverse("token-refresh"), {"refresh": old_refresh}, format="json"
    )

    assert response.data["refresh"] != old_refresh


@pytest.mark.django_db
def test_token_refresh_rejects_reused_refresh_token_after_rotation(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
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
def test_token_refresh_ignores_an_expired_access_token_in_the_header(
    api_client: APIClient,
) -> None:
    refresh = RefreshToken.for_user(UserFactory.create(email="просрочен@example.com"))
    access = refresh.access_token
    access.set_exp(lifetime=timedelta(seconds=-1))
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.post(
        reverse("token-refresh"), {"refresh": str(refresh)}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_token_verify_returns_200_for_a_valid_access_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
    access = str(RefreshToken.for_user(user).access_token)

    response = api_client.post(
        reverse("token-verify"), {"token": access}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_token_verify_returns_401_for_an_expired_access_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
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


@pytest.mark.django_db
def test_me_returns_the_authenticated_users_profile(api_client: APIClient) -> None:
    user = UserFactory.create(
        email="user@example.com",
        first_name="Имя",
        last_name="Фамилия",
        avatar="https://example.com/avatar/user.jpg",
    )
    access = str(RefreshToken.for_user(user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get(reverse("auth-me"))

    assert response.data == {
        "email": "user@example.com",
        "display_name": "Имя Фамилия",
        "avatar": "https://example.com/avatar/user.jpg",
    }


@pytest.mark.django_db
def test_me_returns_401_for_an_unauthenticated_request(api_client: APIClient) -> None:
    response = api_client.get(reverse("auth-me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_delete_returns_204(api_client: APIClient) -> None:
    user = UserFactory.create(email="уходящий@example.com")
    access = str(RefreshToken.for_user(user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.delete(reverse("auth-me"))

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_me_delete_returns_401_for_an_unauthenticated_request(
    api_client: APIClient,
) -> None:
    response = api_client.delete(reverse("auth-me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_refresh_returns_401_after_the_account_was_deleted(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="бывший@example.com")
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.delete(reverse("auth-me"))
    api_client.credentials()

    response = api_client.post(
        reverse("token-refresh"), {"refresh": str(refresh)}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_refresh_returns_401_for_a_token_that_outlived_its_user(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="удалённый-админом@example.com")
    refresh = str(RefreshToken.for_user(user))
    user.delete()

    response = api_client.post(
        reverse("token-refresh"), {"refresh": refresh}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_returns_401_with_an_access_token_of_a_deleted_account(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="исчезнувший@example.com")
    access = str(RefreshToken.for_user(user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    api_client.delete(reverse("auth-me"))

    response = api_client.get(reverse("auth-me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_returns_204(api_client: APIClient) -> None:
    user = UserFactory.create(email="user@example.com")
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    response = api_client.post(
        reverse("auth-logout"), {"refresh": str(refresh)}, format="json"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_logout_returns_401_for_an_unauthenticated_request(
    api_client: APIClient,
) -> None:
    response = api_client.post(
        reverse("auth-logout"), {"refresh": "не-настоящий-токен"}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_returns_401_for_a_malformed_refresh_token(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
    access = str(RefreshToken.for_user(user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.post(
        reverse("auth-logout"), {"refresh": "не-настоящий-токен"}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_refresh_returns_401_after_the_token_was_blacklisted_via_logout(
    api_client: APIClient,
) -> None:
    user = UserFactory.create(email="user@example.com")
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.post(reverse("auth-logout"), {"refresh": str(refresh)}, format="json")

    response = api_client.post(
        reverse("token-refresh"), {"refresh": str(refresh)}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_schema_documents_google_auth_success_response(api_client: APIClient) -> None:
    response = api_client.get(reverse("schema"), {"format": "json"})

    assert response.json()["paths"][reverse("auth-google")]["post"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/GoogleAuthResponse"
    }


def test_schema_documents_google_auth_bad_request_response(
    api_client: APIClient,
) -> None:
    response = api_client.get(reverse("schema"), {"format": "json"})

    assert (
        "400" in response.json()["paths"][reverse("auth-google")]["post"]["responses"]
    )


def test_schema_documents_google_auth_forbidden_response(
    api_client: APIClient,
) -> None:
    response = api_client.get(reverse("schema"), {"format": "json"})

    assert (
        "403" in response.json()["paths"][reverse("auth-google")]["post"]["responses"]
    )


def test_schema_documents_me_response_as_user_profile(api_client: APIClient) -> None:
    response = api_client.get(reverse("schema"), {"format": "json"})

    assert response.json()["paths"][reverse("auth-me")]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"] == {"$ref": "#/components/schemas/UserProfile"}


def test_schema_documents_me_deletion_as_returning_no_content(
    api_client: APIClient,
) -> None:
    response = api_client.get(reverse("schema"), {"format": "json"})

    assert "204" in response.json()["paths"][reverse("auth-me")]["delete"]["responses"]


def test_schema_documents_logout_as_returning_no_content(api_client: APIClient) -> None:
    response = api_client.get(reverse("schema"), {"format": "json"})

    assert (
        "204" in response.json()["paths"][reverse("auth-logout")]["post"]["responses"]
    )
