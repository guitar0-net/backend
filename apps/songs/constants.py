# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Constants for the songs app."""

from django.db import models


class SizeChoice(models.IntegerChoices):
    """Five-step size scale: 1 = smallest, 3 = default, 5 = largest."""

    XS = 1, "Очень маленький"
    SM = 2, "Маленький"
    MD = 3, "Средний"
    LG = 4, "Большой"
    XL = 5, "Очень большой"


class ChordOrientationChoice(models.TextChoices):
    """Chord diagram orientation for PDF output."""

    HORIZONTAL = "horizontal", "Горизонтальный"
    VERTICAL = "vertical", "Вертикальный"
