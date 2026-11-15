# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Constants for the reports app."""

from collections.abc import Mapping
from typing import Final

from django.db import models


class ReportTargetType(models.TextChoices):
    """What a report is about.

    APP covers everything not tied to one content item: a broken screen, a
    crash, a feature request. Comments will join here once they exist.
    """

    SONG = "song", "Песня"
    LESSON = "lesson", "Урок"
    COURSE = "course", "Курс"
    CHORD = "chord", "Аккорд"
    SCHEME = "scheme", "Бой или схема"
    APP = "app", "Приложение"


class ReportReason(models.TextChoices):
    """Why the user is reporting.

    Codes are never removed: the server accepts any of them for any target
    type, so a report queued offline against an older reason list still goes
    through, and stored reports keep a valid reason. To retire a reason, drop
    it from REASONS_BY_TARGET_TYPE instead.
    """

    WRONG_CHORDS = "wrong_chords", "Неверные аккорды"
    WRONG_LYRICS = "wrong_lyrics", "Ошибка в тексте песни"
    WRONG_RHYTHM = "wrong_rhythm", "Неверный бой или ритм"
    WRONG_FINGERING = "wrong_fingering", "Неверная аппликатура"
    CONTENT_ERROR = "content_error", "Ошибка в содержании"
    TYPO = "typo", "Опечатка"
    BROKEN_MEDIA = "broken_media", "Не загружается картинка или видео"
    DISPLAY_ISSUE = "display_issue", "Неправильно отображается"
    BUG = "bug", "Ошибка в приложении"
    FEATURE_REQUEST = "feature_request", "Предложить функцию"
    OTHER = "other", "Другое"


REASONS_BY_TARGET_TYPE: Final[Mapping[str, tuple[ReportReason, ...]]] = {
    ReportTargetType.SONG: (
        ReportReason.WRONG_CHORDS,
        ReportReason.WRONG_LYRICS,
        ReportReason.WRONG_RHYTHM,
        ReportReason.DISPLAY_ISSUE,
        ReportReason.OTHER,
    ),
    ReportTargetType.LESSON: (
        ReportReason.CONTENT_ERROR,
        ReportReason.TYPO,
        ReportReason.BROKEN_MEDIA,
        ReportReason.DISPLAY_ISSUE,
        ReportReason.OTHER,
    ),
    ReportTargetType.COURSE: (
        ReportReason.CONTENT_ERROR,
        ReportReason.TYPO,
        ReportReason.DISPLAY_ISSUE,
        ReportReason.OTHER,
    ),
    ReportTargetType.CHORD: (
        ReportReason.WRONG_FINGERING,
        ReportReason.DISPLAY_ISSUE,
        ReportReason.OTHER,
    ),
    ReportTargetType.SCHEME: (
        ReportReason.WRONG_RHYTHM,
        ReportReason.BROKEN_MEDIA,
        ReportReason.OTHER,
    ),
    ReportTargetType.APP: (
        ReportReason.BUG,
        ReportReason.FEATURE_REQUEST,
        ReportReason.OTHER,
    ),
}
"""Reasons a client offers for each target type, in display order.

Controls what the client shows, not what the server accepts, so reasons
can be reordered or hidden without breaking reports already queued.
"""

REASONS_REQUIRING_MESSAGE: Final[frozenset[str]] = frozenset({
    ReportReason.OTHER,
    ReportReason.FEATURE_REQUEST,
})
"""Reasons that say nothing on their own, so the user must describe the issue.

The server rejects these without a message, so this set may only shrink:
adding a reason would turn reports queued without a message into 400s,
which the client drops.
"""


CONTENT_VERSIONED_TARGET_TYPES: Final[frozenset[str]] = frozenset({
    ReportTargetType.SONG,
    ReportTargetType.LESSON,
})
"""Target types whose edits move the sync content version.

Only for these can a report's `content_version` be compared with its
`target_updated_at`: song edits propagate to `Lesson.updated_at`, which the
version is derived from. Course edits do not, and chords and schemes have no
`updated_at` of their own to compare with.
"""


class ReportStatus(models.TextChoices):
    """Staff-side processing state of a report."""

    NEW = "new", "Новый"
    IN_PROGRESS = "in_progress", "В работе"
    RESOLVED = "resolved", "Исправлено"
    REJECTED = "rejected", "Отклонено"


class ClientPlatform(models.TextChoices):
    """Client the report was sent from."""

    ANDROID = "android", "Android"
    IOS = "ios", "iOS"
    WEB = "web", "Web"


# Reports are written by anonymous callers, so the shared anon rate (per
# minute) would let one device flood the staff inbox. The per-IP scope stays
# loose because carriers put many subscribers behind one address.
REPORT_CREATE_THROTTLE_SCOPE = "report_create"
REPORT_DEVICE_THROTTLE_SCOPE = "report_create_device"
