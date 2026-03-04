# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for announcements selectors."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.announcements.selectors import get_published_announcements
from apps.announcements.tests.factories import AnnouncementFactory


@pytest.mark.django_db
def test_get_published_announcements_excludes_unpublished() -> None:
    # Published
    AnnouncementFactory.create(
        title="Published", published_at=timezone.now() - timedelta(minutes=1)
    )
    # Scheduled for future
    AnnouncementFactory.create(
        title="Future", published_at=timezone.now() + timedelta(days=1)
    )
    # Draft
    AnnouncementFactory.create(title="Draft", published_at=None)

    announcements = get_published_announcements()

    assert announcements.count() == 1
    announcement = announcements.first()
    assert announcement
    assert announcement.title == "Published"


@pytest.mark.django_db
def test_get_published_announcements_returns_all_published() -> None:
    now = timezone.now()
    AnnouncementFactory.create(published_at=now - timedelta(days=1))
    AnnouncementFactory.create(published_at=now - timedelta(hours=1))
    AnnouncementFactory.create(published_at=now + timedelta(days=1))  # Future
    AnnouncementFactory.create(published_at=None)  # Draft

    announcements = get_published_announcements()

    assert announcements.count() == 2
