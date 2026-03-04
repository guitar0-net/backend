# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factory for generating test Announcement instances."""

from django.utils import timezone
from factory import Faker  # type: ignore[attr-defined]
from factory.django import DjangoModelFactory

from apps.announcements.models import Announcement


class AnnouncementFactory(DjangoModelFactory[Announcement]):
    """Factory for creating Announcement instances with realistic data."""

    title = Faker("sentence", nb_words=4)
    slug = Faker("slug")
    content = Faker("paragraph", nb_sentences=3)
    product_version = Faker("numerify", text="##.##.##")
    published_at = timezone.now()

    class Meta:
        model = Announcement
        skip_postgeneration_save = True
