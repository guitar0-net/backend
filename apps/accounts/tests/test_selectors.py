# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for accounts selectors."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors import (
    get_active_refresh_tokens,
    get_social_account,
    get_user_by_email,
)
from apps.accounts.tests.factories.social_account import SocialAccountFactory
from apps.accounts.tests.factories.user import UserFactory


@pytest.mark.django_db
def test_get_user_by_email_finds_user_case_insensitively() -> None:
    UserFactory.create(email="Guitarist@example.com")
    assert get_user_by_email("guitarist@example.com") is not None


@pytest.mark.django_db
def test_get_user_by_email_returns_none_when_no_match() -> None:
    assert get_user_by_email("nobody@example.com") is None


@pytest.mark.django_db
def test_get_social_account_finds_account_by_provider_and_uid() -> None:
    SocialAccountFactory.create(provider="google-oauth2", provider_uid="uid-Ж-42")
    account = get_social_account("google-oauth2", "uid-Ж-42")
    assert account is not None


@pytest.mark.django_db
def test_get_social_account_returns_none_when_no_match() -> None:
    assert get_social_account("google-oauth2", "does-not-exist") is None


@pytest.mark.django_db
def test_get_active_refresh_tokens_returns_tokens_issued_to_the_user() -> None:
    user = UserFactory.create(email="ученик@example.com")
    refresh = RefreshToken.for_user(user)
    assert list(get_active_refresh_tokens(user).values_list("jti", flat=True)) == [
        refresh["jti"]
    ]


@pytest.mark.django_db
def test_get_active_refresh_tokens_excludes_blacklisted_tokens() -> None:
    user = UserFactory.create(email="ушедший@example.com")
    RefreshToken.for_user(user).blacklist()
    assert not get_active_refresh_tokens(user).exists()


@pytest.mark.django_db
def test_get_active_refresh_tokens_excludes_other_users_tokens() -> None:
    user = UserFactory.create(email="первый@example.com")
    RefreshToken.for_user(UserFactory.create(email="второй@example.com"))
    assert not get_active_refresh_tokens(user).exists()
