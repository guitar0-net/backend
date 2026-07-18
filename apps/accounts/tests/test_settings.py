# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for accounts-related Django settings (JWT, Google auth)."""

from datetime import timedelta

import pytest
from django.conf import settings


def test_simple_jwt_access_token_lifetime() -> None:
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(minutes=60)


def test_simple_jwt_refresh_token_lifetime() -> None:
    assert settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] == timedelta(days=30)


def test_simple_jwt_refresh_token_rotation_enabled() -> None:
    assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True


def test_simple_jwt_blacklist_after_rotation_enabled() -> None:
    assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True


def test_token_blacklist_app_is_installed() -> None:
    assert "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS


def test_jwt_authentication_is_registered_for_the_api() -> None:
    assert (
        "rest_framework_simplejwt.authentication.JWTAuthentication"
        in settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
    )


def test_google_client_id_setting_exists() -> None:
    assert hasattr(settings, "GOOGLE_CLIENT_ID")


@pytest.mark.django_db
def test_simplejwt_token_blacklist_tables_exist() -> None:
    from django.db import connection

    tables = connection.introspection.table_names()
    assert "token_blacklist_blacklistedtoken" in tables
