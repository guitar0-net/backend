# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shared fixtures for accounts app tests."""

import pytest


@pytest.fixture(autouse=True)
def _configure_google_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a GOOGLE_CLIENT_ID so Google auth tests reach real token verification.

    Tests that specifically exercise the missing-configuration guard override
    this back to None themselves.
    """
    monkeypatch.setattr(
        "apps.accounts.services.settings.GOOGLE_CLIENT_ID", "test-google-client-id"
    )
