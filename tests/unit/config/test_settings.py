# SPDX-FileCopyrightText: 2025-2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import importlib
import random
import sys
import types
from collections.abc import Generator
from pathlib import Path

import pytest
from pydantic import ValidationError

from config.settings.base import Settings, get_settings


@pytest.fixture
def env_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Generator[Path]:
    for var in ["SECRET_KEY", "DATABASE_URL", "DEBUG", "ENVIRONMENT", "ALLOWED_HOSTS"]:
        monkeypatch.delenv(var, raising=False)
    env_path = tmp_path / ".env.development"
    env_path.write_text(
        "SECRET_KEY=secret-key\n"
        "DATABASE_URL=sqlite:///db.sqlite3\n"
        "DEBUG=True\n"
        "ENVIRONMENT=development\n"
        """ALLOWED_HOSTS='["localhost","127.0.0.1"]'"""
    )
    monkeypatch.chdir(tmp_path)
    yield env_path


def test_settings_load_from_env(env_file: Path) -> None:
    settings = Settings(_env_file=env_file)  # pyright: ignore[reportCallIssue]
    assert settings.SECRET_KEY == "secret-key"
    assert settings.DATABASE_URL == "sqlite:///db.sqlite3"
    assert settings.DEBUG is True
    assert settings.ENVIRONMENT == "development"
    assert "localhost" in settings.ALLOWED_HOSTS


def test_settings_required_fields_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for var in ["SECRET_KEY", "DATABASE_URL", "DEBUG", "ENVIRONMENT", "ALLOWED_HOSTS"]:
        monkeypatch.delenv(var, raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text("Debug=False")
    with pytest.raises(ValidationError):
        Settings(_env_file=env_path)  # pyright: ignore[reportCallIssue]


def test_env_file_priority(monkeypatch: pytest.MonkeyPatch, env_file: Path) -> None:
    for var in ["SECRET_KEY", "DATABASE_URL", "DEBUG", "ENVIRONMENT", "ALLOWED_HOSTS"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("SECRET_KEY", "environment-secret-key")
    settings = Settings(_env_file=env_file)  # pyright: ignore[reportCallIssue]
    assert settings.SECRET_KEY == "environment-secret-key"


@pytest.fixture
def production_settings_module(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[types.ModuleType]:
    """Reload config.settings with a randomly chosen staging/production environment."""
    environment = random.choice(["staging", "production"])
    monkeypatch.setenv("ENVIRONMENT", environment)
    monkeypatch.setenv("SECRET_KEY", "тест-ключ-123")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///тест-бд.sqlite3")
    get_settings.cache_clear()
    saved_module = sys.modules.pop("config.settings", None)
    try:
        yield importlib.import_module("config.settings")
    finally:
        sys.modules.pop("config.settings", None)
        if saved_module is not None:
            sys.modules["config.settings"] = saved_module
        get_settings.cache_clear()


def test_secure_proxy_ssl_header_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.SECURE_PROXY_SSL_HEADER == (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


def test_session_cookie_secure_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.SESSION_COOKIE_SECURE is True


def test_csrf_cookie_secure_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.CSRF_COOKIE_SECURE is True


def test_hsts_seconds_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.SECURE_HSTS_SECONDS == 31536000


def test_hsts_include_subdomains_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.SECURE_HSTS_INCLUDE_SUBDOMAINS is True


def test_hsts_preload_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.SECURE_HSTS_PRELOAD is True


def test_referrer_policy_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert (
        production_settings_module.SECURE_REFERRER_POLICY
        == "strict-origin-when-cross-origin"
    )


def test_rest_framework_json_only_renderer_set_for_production_environment(
    production_settings_module: types.ModuleType,
) -> None:
    assert production_settings_module.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] == [
        "rest_framework.renderers.JSONRenderer"
    ]
