# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for accounts services."""

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError
from google.auth import exceptions as google_auth_exceptions

from apps.accounts.models.social_account import SocialAccount
from apps.accounts.selectors import get_social_account as real_get_social_account
from apps.accounts.services import (
    InvalidGoogleTokenError,
    authenticate_via_google,
    verify_google_id_token,
)
from apps.accounts.tests.factories.social_account import SocialAccountFactory
from apps.accounts.tests.factories.user import UserFactory


def _stub_claims(
    monkeypatch: pytest.MonkeyPatch,
    *,
    sub: str = "10203040",
    email: str = "жанна@example.com",
) -> None:
    monkeypatch.setattr(
        "apps.accounts.services.verify_google_id_token",
        lambda id_token: {
            "sub": sub,
            "email": email,
            "email_verified": True,
            "given_name": "Жанна",
            "family_name": "Кузнецова",
            "picture": "https://example.com/avatar/zhanna.jpg",
        },
    )


@pytest.mark.django_db
def test_authenticate_via_google_creates_new_user_from_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_claims(monkeypatch)

    user, _created = authenticate_via_google("stub-token")

    assert user.email == "жанна@example.com"


@pytest.mark.django_db
def test_authenticate_via_google_does_not_duplicate_known_sub(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_claims(monkeypatch, sub="55667788")
    authenticate_via_google("stub-token")

    _user, created = authenticate_via_google("stub-token")

    assert not created
    assert SocialAccount.objects.filter(provider_uid="55667788").count() == 1


@pytest.mark.django_db
def test_authenticate_via_google_links_existing_user_found_by_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = UserFactory.create(
        email="давид@example.com", first_name="Давид", last_name="Орлов"
    )
    _stub_claims(monkeypatch, sub="99001122", email="давид@example.com")

    user, created = authenticate_via_google("stub-token")

    assert not created
    assert user.pk == existing.pk


@pytest.mark.django_db
def test_authenticate_via_google_does_not_overwrite_existing_users_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    UserFactory.create(email="давид@example.com", first_name="Давид", last_name="Орлов")
    _stub_claims(monkeypatch, sub="99001122", email="давид@example.com")

    user, _created = authenticate_via_google("stub-token")

    assert user.first_name == "Давид"


@pytest.mark.django_db
def test_authenticate_via_google_stores_raw_claims_in_social_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_claims(monkeypatch, sub="13579")

    authenticate_via_google("stub-token")

    account = SocialAccount.objects.get(provider_uid="13579")
    assert account.extra_data["given_name"] == "Жанна"


@pytest.mark.django_db
def test_authenticate_via_google_raises_on_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(*_args: object, **_kwargs: object) -> None:
        raise ValueError("Token used too late")

    monkeypatch.setattr(
        "apps.accounts.services.google_id_token.verify_oauth2_token", _raise
    )

    with pytest.raises(InvalidGoogleTokenError):
        authenticate_via_google("expired-token")


@pytest.mark.django_db
def test_authenticate_via_google_raises_on_wrong_issuer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(*_args: object, **_kwargs: object) -> None:
        raise google_auth_exceptions.GoogleAuthError("Wrong issuer")  # type: ignore[no-untyped-call]

    monkeypatch.setattr(
        "apps.accounts.services.google_id_token.verify_oauth2_token", _raise
    )

    with pytest.raises(InvalidGoogleTokenError):
        authenticate_via_google("forged-token")


@pytest.mark.django_db
def test_authenticate_via_google_raises_on_unverified_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "apps.accounts.services.verify_google_id_token",
        lambda id_token: {
            "sub": "13570",
            "email": "жанна@example.com",
            "email_verified": False,
            "given_name": "Жанна",
            "family_name": "Кузнецова",
            "picture": "https://example.com/avatar/zhanna.jpg",
        },
    )

    with pytest.raises(InvalidGoogleTokenError):
        authenticate_via_google("stub-token")


def test_verify_google_id_token_raises_when_client_id_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("apps.accounts.services.settings.GOOGLE_CLIENT_ID", None)

    with pytest.raises(ImproperlyConfigured):
        verify_google_id_token("irrelevant-token")


def _miss_first_lookup_then_delegate(
    monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    """Make the first call to `target` return None, then behave normally.

    Simulates a concurrent request having already committed by the time a
    later step (e.g. the DB insert) runs, even though the initial read
    missed it — without needing a second real DB connection.
    """
    calls: list[object] = []

    def _stub(provider: str, provider_uid: str) -> SocialAccount | None:
        calls.append(1)
        if len(calls) == 1:
            return None
        return real_get_social_account(provider, provider_uid)

    monkeypatch.setattr(target, _stub)


@pytest.mark.django_db
def test_authenticate_via_google_returns_winners_user_when_social_account_create_races(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_claims(monkeypatch, sub="24681012", email="запрос@example.com")
    winner = UserFactory.create(email="победитель@example.com")
    SocialAccountFactory.create(
        user=winner, provider="google-oauth2", provider_uid="24681012"
    )
    _miss_first_lookup_then_delegate(
        monkeypatch, "apps.accounts.services.get_social_account"
    )

    user, _created = authenticate_via_google("stub-token")

    assert user.pk == winner.pk


@pytest.mark.django_db
def test_authenticate_via_google_returns_winners_user_when_new_user_email_races(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_claims(monkeypatch, sub="99887766", email="гонка@example.com")
    winner = UserFactory.create(email="гонка@example.com")
    SocialAccountFactory.create(
        user=winner, provider="google-oauth2", provider_uid="99887766"
    )
    _miss_first_lookup_then_delegate(
        monkeypatch, "apps.accounts.services.get_social_account"
    )
    monkeypatch.setattr("apps.accounts.services.get_user_by_email", lambda email: None)

    user, _created = authenticate_via_google("stub-token")

    assert user.pk == winner.pk


@pytest.mark.django_db
def test_authenticate_via_google_reraises_integrity_error_without_a_winner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_claims(monkeypatch, sub="11223344")

    def _raise(**_kwargs: object) -> None:
        raise IntegrityError("unexpected constraint violation")

    monkeypatch.setattr("apps.accounts.services.SocialAccount.objects.create", _raise)

    with pytest.raises(IntegrityError):
        authenticate_via_google("stub-token")
