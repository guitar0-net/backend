# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Models for the lessons app."""

from __future__ import annotations

import uuid

from django.db import models

from apps.songs.models import Song


class Lesson(models.Model):
    """Educational lesson entity."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    title = models.CharField(
        "Название",
        max_length=200,
    )

    description = models.TextField(
        "Описание",
        blank=True,
        help_text="Краткое описание содержания урока",
    )

    video_url = models.URLField(
        "Видео",
        help_text="Ссылка на видео урока",
    )

    duration = models.PositiveIntegerField(
        "Длительность (сек)",
        default=0,
        help_text="Общая длительность урока в секундах",
    )

    songs = models.ManyToManyField(
        Song,
        verbose_name="Песни",
        blank=True,
        related_name="lessons",
        help_text="Песни, которые разбираются в уроке",
    )

    addition_lessons: models.ManyToManyField[Lesson, Lesson] = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="recommended_for",
        verbose_name="Рекомендуемые дополнительные уроки",
    )

    is_published = models.BooleanField(
        "Опубликован",
        default=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self) -> str:
        return f"Lesson: '{self.title}'"
