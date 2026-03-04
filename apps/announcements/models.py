# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Models for the announcements app."""

import uuid
from typing import ClassVar

from django.db import models
from markdownx.models import MarkdownxField  # type: ignore[import-untyped]


class Announcement(models.Model):
    """Model representing a product announcement or news entry.

    Attributes:
        uuid (UUID): Unique public identifier for the announcement.
        title (str): Headline of the announcement.
        slug (str): URL-friendly identifier, unique per announcement.
        content (str): Full Markdown-formatted body text.
        product_version (str): Optional product version tag (e.g. "1.2.0").
        published_at (datetime): Timestamp when the announcement will be published.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp of the last update.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    title = models.CharField(
        "Заголовок",
        max_length=200,
    )

    slug = models.SlugField(
        "Slug",
        max_length=200,
        unique=True,
    )

    content = MarkdownxField("Содержание")

    product_version = models.CharField(
        "Версия продукта",
        max_length=50,
        blank=True,
        help_text="Например: 1.2.0",
    )

    published_at = models.DateTimeField(
        "Дата-время публикации",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "Дата обновления",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return f"Announcement: '{self.title}'"
