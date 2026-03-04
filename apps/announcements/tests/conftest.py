# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures for testing announcements app."""

import pytest

from apps.announcements.models import Announcement
from apps.announcements.tests.factories import AnnouncementFactory


@pytest.fixture
def announcement() -> Announcement:
    """Fixture creating an announcement for testing.

    Returns:
        Announcement: announcement instance
    """
    return AnnouncementFactory.create()
