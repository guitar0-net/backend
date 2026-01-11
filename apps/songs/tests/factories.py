# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later


"""Factory for generating tests of Song instances."""

import factory
from factory import Faker, Sequence  # type: ignore[attr-defined]
from factory.django import DjangoModelFactory

from apps.chords.models import Chord
from apps.chords.tests.factories import ChordFactory
from apps.schemes.models import ImageScheme
from apps.schemes.tests.factories import ImageSchemeFactory
from apps.songs.models import Song


class SongFactory(DjangoModelFactory[Song]):
    """Factory for creating Song instances."""

    title = Sequence(lambda n: f"Song {n}")
    text = Faker(
        "paragraph",
        nb_sentences=3,
    )
    metronome = Faker(
        "random_int",
        min=60,
        max=180,
    )

    @factory.post_generation  # type: ignore[misc, attr-defined]
    def chords(
        self,
        create: bool,
        extracted: int | list[Chord] | None,
    ) -> None:
        """Create chords for song.

        Usage:
        - SongFactory(chords=[chord1, chord2])
        - SongFactory(chords=3)
        """
        if not create:
            return

        if extracted is None:
            return

        if isinstance(extracted, int):
            self.chords.add(*ChordFactory.create_batch(extracted))
        else:
            self.chords.add(*extracted)

    @factory.post_generation  # type: ignore[misc, attr-defined]
    def schemes(
        self,
        create: bool,
        extracted: int | list[ImageScheme] | None,
    ) -> None:
        """Create schemes for song.

        Usage:
        - SongFactory(schemes=[scheme1])
        - SongFactory(schemes=2)
        """
        if not create:
            return

        if extracted is None:
            return

        if isinstance(extracted, int):
            self.schemes.add(*ImageSchemeFactory.create_batch(extracted))
        else:
            self.schemes.add(*extracted)

    class Meta:
        model = Song
        skip_postgeneration_save = True
        django_get_or_create = ("title",)
