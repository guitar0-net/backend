# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for Announcement model."""

import uuid

import pytest

from apps.announcements.models import Announcement
from apps.announcements.tests.factories import AnnouncementFactory


@pytest.mark.django_db
def test_announcement_factory_creates_announcement() -> None:
    announcement = AnnouncementFactory.create()

    assert announcement.pk is not None
    assert announcement.title
    assert announcement.slug
    assert announcement.uuid
    assert announcement.content


@pytest.mark.django_db
def test_announcement_uuid_is_auto_generated() -> None:
    announcement = AnnouncementFactory.create()

    assert isinstance(announcement.uuid, uuid.UUID)


@pytest.mark.django_db
def test_announcement_uuid_is_unique() -> None:
    a1 = AnnouncementFactory.create()
    a2 = AnnouncementFactory.create()

    assert a1.uuid != a2.uuid


@pytest.mark.django_db
def test_announcement_str_method() -> None:
    announcement = AnnouncementFactory.create(title="New Feature")

    assert str(announcement) == "Announcement: 'New Feature'"


@pytest.mark.django_db
def test_announcement_timestamps_are_set() -> None:
    announcement = AnnouncementFactory.create()

    assert announcement.created_at is not None
    assert announcement.updated_at is not None


@pytest.mark.django_db
def test_announcement_slug_is_unique() -> None:
    AnnouncementFactory.create(slug="unique-slug")

    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        AnnouncementFactory.create(slug="unique-slug")


@pytest.mark.django_db
def test_announcement_product_version_can_be_blank() -> None:
    announcement = AnnouncementFactory.create(product_version="")

    assert not announcement.product_version


@pytest.mark.django_db
def test_announcement_ordering_newest_first() -> None:
    a1 = AnnouncementFactory.create(title="First")
    a2 = AnnouncementFactory.create(title="Second")
    a3 = AnnouncementFactory.create(title="Third")

    announcements = list(Announcement.objects.all())

    assert announcements == [a3, a2, a1]
