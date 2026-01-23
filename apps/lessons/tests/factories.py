# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factory for generating test Lesson instances."""

import factory
from factory import Faker  # type: ignore[attr-defined]
from factory.django import DjangoModelFactory

from apps.lessons.models import Lesson
from apps.songs.models import Song
from apps.songs.tests.factories import SongFactory


class LessonFactory(DjangoModelFactory[Lesson]):
    """Factory for creating Lesson instances."""

    title = Faker("sentence", nb_words=3)
    description = Faker("paragraph", nb_sentences=2)
    video_url = Faker("url")
    duration = Faker("random_int", min=30, max=3600)
    is_published = True

    @factory.post_generation  # type: ignore[misc, attr-defined]
    def songs(
        self,
        create: bool,
        extracted: int | list[Song] | None,
    ) -> None:
        """Create songs for lesson.

        Usage:
        - LessonFactory(songs=[song1, song2])
        - LessonFactory(songs=3)
        """
        if not create:
            return

        if extracted is None:
            return

        if isinstance(extracted, int):
            self.songs.add(*SongFactory.create_batch(extracted))
        else:
            self.songs.add(*extracted)

    @factory.post_generation  # type: ignore[misc, attr-defined]
    def addition_lessons(
        self,
        create: bool,
        extracted: int | list[Lesson] | None,
    ) -> None:
        """Create additional recommended lessons.

        Usage:
        - LessonFactory(addition_lessons=[lesson1, lesson2])
        - LessonFactory(addition_lessons=3)
        """
        if not create:
            return

        if extracted is None:
            return

        if isinstance(extracted, int):
            self.addition_lessons.add(*LessonFactory.create_batch(extracted))
        else:
            self.addition_lessons.add(*extracted)

    class Meta:
        model = Lesson
        skip_postgeneration_save = True
