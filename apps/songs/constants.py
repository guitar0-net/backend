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


SONG_PRINT_THROTTLE_SCOPE = "song_print"

SONG_TEXT_SCHEMA_DESCRIPTION = (
    "Deprecated: no longer maintained, use `chord_text`. Markdown with chords on "
    "separate bold lines aligned by spaces, so they drift from the lyrics when a "
    "line wraps. Kept for released app versions; may be empty for new songs."
)

SONG_CHORD_TEXT_SCHEMA_DESCRIPTION = (
    "Song text in markdown with every chord written inline in square brackets "
    "right before the syllable it belongs to: `Мы не [G (2)]знали друг друга`. "
    "A chord after the last word goes at the end of the line after a space. "
    "Text inside the brackets after the chord name (from a space or `(`) is a "
    "performance note such as a strum count. Chord-only lines (intros, "
    "instrumentals) stay bold lines without brackets. Brackets are markdown "
    "link syntax (`[Am](…)`), so cut the chords out before rendering markdown. "
    "Empty string when the song is not converted yet: fall back to `text`."
)
