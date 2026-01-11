# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Models for the songs app."""

from django.db import models
from markdownx.models import MarkdownxField  # type: ignore[import-untyped]

from apps.chords.models import Chord
from apps.schemes.models import ImageScheme


class Song(models.Model):
    """Main model for song."""

    title = models.CharField("Название", max_length=200)
    chords = models.ManyToManyField(Chord, verbose_name="Аккорды", blank=True)
    schemes = models.ManyToManyField(
        ImageScheme, verbose_name="Ритмические рисунки (изображения)", blank=True
    )
    text = MarkdownxField("Текст песни", help_text="С аккордами и переносами строк")
    metronome = models.IntegerField("Метроном", default=0)

    class Meta:
        verbose_name = "Песня"
        verbose_name_plural = "Песни"

    def __str__(self) -> str:
        return self.title
