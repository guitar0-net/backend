# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SocialAccount model."""

from typing import ClassVar

from django.conf import settings
from django.db import models


class SocialAccount(models.Model):
    """Stores a social-provider identity linked to a user account.

    One user may have multiple social accounts (one per provider).
    The combination of provider and provider_uid is globally unique.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_accounts",
        verbose_name="Пользователь",
    )
    provider = models.CharField("Провайдер", max_length=64)
    provider_uid = models.CharField("UID провайдера", max_length=255)
    extra_data = models.JSONField("Дополнительные данные", default=dict)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Социальный аккаунт"
        verbose_name_plural = "Социальные аккаунты"
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["provider", "provider_uid"],
                name="unique_provider_uid",
            )
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_uid}"
