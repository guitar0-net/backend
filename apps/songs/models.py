# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Models for the songs app."""

import uuid

from django.db import models
from markdownx.models import MarkdownxField  # type: ignore[import-untyped]

from apps.chords.models import Chord
from apps.schemes.models import ImageScheme


class Song(models.Model):
    """Main model for song."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField("Название", max_length=200)
    chords = models.ManyToManyField(Chord, verbose_name="Аккорды", blank=True)
    schemes = models.ManyToManyField(
        ImageScheme, verbose_name="Ритмические рисунки (изображения)", blank=True
    )
    text = MarkdownxField(
        "Текст песни (устарело)",
        blank=True,
        help_text=(
            "Устарело, больше не поддерживается: заполняйте «Текст с аккордами». "
            "Поле читают только старые версии приложения."
        ),
    )
    chord_text = MarkdownxField(
        "Текст с аккордами",
        blank=True,
        default="",
        help_text=(
            "Аккорд в квадратных скобках прямо перед слогом: "
            "«Мы не [G (2)]знали друг друга». Аккорд после последнего слова — "
            "в конце строки через пробел. Строки только из аккордов "
            "(вступление, проигрыш) остаются жирными, как в старом тексте."
        ),
    )
    metronome = models.IntegerField("Метроном", default=0)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Песня"
        verbose_name_plural = "Песни"

    def __str__(self) -> str:
        return self.title
