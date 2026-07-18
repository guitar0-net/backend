# SPDX-FileCopyrightText: 2025-2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for User."""

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models.user import User
from apps.accounts.tests.factories.user import UserFactory


@pytest.mark.django_db
def test_user_model_configuration(user_factory: type[UserFactory]) -> None:
    user = user_factory.create()
    assert get_user_model() == User
    assert User.USERNAME_FIELD == "email"
    assert User.REQUIRED_FIELDS == []
    assert isinstance(user.email, str)


@pytest.mark.django_db
def test_user_str_representation(user_factory: type[UserFactory]) -> None:
    user = user_factory.create(email="user@example.com")
    assert str(user) == "user@example.com"


@pytest.mark.django_db
def test_user_avatar_accepts_url(user_factory: type[UserFactory]) -> None:
    user = user_factory.create(avatar="https://example.com/avatar/andrey.jpg")
    assert user.avatar == "https://example.com/avatar/andrey.jpg"


@pytest.mark.django_db
def test_user_avatar_defaults_to_empty(user_factory: type[UserFactory]) -> None:
    user = user_factory.create()
    assert not user.avatar


@pytest.mark.django_db
def test_display_name_combines_first_and_last_name_when_both_are_set(
    user_factory: type[UserFactory],
) -> None:
    user = user_factory.create(first_name="Имя", last_name="Фамилия")
    assert user.display_name == "Имя Фамилия"


@pytest.mark.django_db
def test_display_name_uses_only_first_name_when_last_name_is_blank(
    user_factory: type[UserFactory],
) -> None:
    user = user_factory.create(first_name="Имя", last_name="")
    assert user.display_name == "Имя"


@pytest.mark.django_db
def test_display_name_falls_back_to_email_prefix_when_no_name_is_set(
    user_factory: type[UserFactory],
) -> None:
    user = user_factory.create(first_name="", last_name="", email="person@example.com")
    assert user.display_name == "person"
