# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for custom authentication classes."""

from datetime import timedelta

import pytest
from faker import Faker
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.tests.factories.user import UserFactory
from apps.shared.authentication import OptionalJWTAuthentication


def _request(authorization: str) -> Request:
    return Request(APIRequestFactory().get("/", HTTP_AUTHORIZATION=authorization))


@pytest.fixture
def fake() -> Faker:
    """Return a Faker producing Cyrillic text."""
    return Faker("ru_RU")


@pytest.mark.django_db
def test_optional_jwt_authentication_identifies_the_holder_of_a_valid_token(
    fake: Faker,
) -> None:
    user = UserFactory.create(email=fake.email())
    token = AccessToken.for_user(user)

    result = OptionalJWTAuthentication().authenticate(_request(f"Bearer {token}"))

    assert result is not None and result[0] == user


@pytest.mark.django_db
def test_optional_jwt_authentication_treats_an_expired_token_as_anonymous(
    fake: Faker,
) -> None:
    token = AccessToken.for_user(UserFactory.create(email=fake.email()))
    token.set_exp(lifetime=-timedelta(minutes=fake.pyint(1, 1000)))

    result = OptionalJWTAuthentication().authenticate(_request(f"Bearer {token}"))

    assert result is None


def test_optional_jwt_authentication_treats_a_malformed_token_as_anonymous(
    fake: Faker,
) -> None:
    result = OptionalJWTAuthentication().authenticate(
        _request(f"Bearer {fake.sha256()}")
    )

    assert result is None


@pytest.mark.django_db
def test_optional_jwt_authentication_treats_a_deleted_user_as_anonymous(
    fake: Faker,
) -> None:
    user = UserFactory.create(email=fake.email())
    token = AccessToken.for_user(user)
    user.delete()

    result = OptionalJWTAuthentication().authenticate(_request(f"Bearer {token}"))

    assert result is None
