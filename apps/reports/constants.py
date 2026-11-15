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
    """Why the user is reporting; which ones apply depends on the target type."""

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
"""Reasons a client may offer for each target type, in display order."""

REASONS_REQUIRING_MESSAGE: Final[frozenset[str]] = frozenset({
    ReportReason.OTHER,
    ReportReason.FEATURE_REQUEST,
})
"""Reasons that say nothing on their own, so the user must describe the issue."""


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
# minute) would let one device flood the staff inbox.
REPORT_CREATE_THROTTLE_SCOPE = "report_create"
