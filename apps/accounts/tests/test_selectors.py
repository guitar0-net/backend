# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for accounts selectors."""

import pytest

from apps.accounts.selectors import get_social_account, get_user_by_email
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
