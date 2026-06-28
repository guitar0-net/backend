# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for SocialAccount model."""

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models.social_account import SocialAccount
from apps.accounts.tests.factories.social_account import SocialAccountFactory
from apps.accounts.tests.factories.user import UserFactory


@pytest.mark.django_db
def test_social_account_can_be_created_with_required_fields() -> None:
    account = SocialAccountFactory.create()
    assert account.pk is not None


@pytest.mark.django_db
def test_social_account_str_representation() -> None:
    account = SocialAccountFactory.create(
        provider="google-oauth2", provider_uid="12345"
    )
    assert str(account) == "google-oauth2:12345"


@pytest.mark.django_db
def test_social_account_created_at_is_set_automatically() -> None:
    before = timezone.now()
    account = SocialAccountFactory.create()
    assert account.created_at >= before


@pytest.mark.django_db
def test_social_account_updated_at_is_set_automatically() -> None:
    before = timezone.now()
    account = SocialAccountFactory.create()
    assert account.updated_at >= before


@pytest.mark.django_db
def test_social_account_unique_constraint_on_provider_and_uid() -> None:
    user = UserFactory.create()
    SocialAccountFactory.create(
        user=user, provider="google-oauth2", provider_uid="uid-duplicate"
    )
    with pytest.raises(IntegrityError):
        SocialAccountFactory.create(
            user=user, provider="google-oauth2", provider_uid="uid-duplicate"
        )


@pytest.mark.django_db
def test_social_account_deleted_when_user_is_deleted() -> None:
    account = SocialAccountFactory.create()
    pk = account.pk
    account.user.delete()
    assert not SocialAccount.objects.filter(pk=pk).exists()
