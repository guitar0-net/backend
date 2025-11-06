# SPDX-FileCopyrightText: 2025 Andrey Kotlyar
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from config.asgi import application as asgi_app
from config.wsgi import application as wsgi_app


def test_wsgi_application() -> None:
    assert wsgi_app is not None


def test_asgi_application() -> None:
    assert asgi_app is not None
