# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the reports app."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from django.db.models import QuerySet

from apps.chords.models import Chord
from apps.courses.models import Course
from apps.lessons.models import Lesson
from apps.reports.constants import ReportTargetType
from apps.reports.models import Report
from apps.schemes.models import ImageScheme
from apps.songs.models import Song


@dataclass(frozen=True, kw_only=True)
class ReportTargetSnapshot:
    """What a report remembers about its target at submission time."""

    title: str
    updated_at: datetime | None


def get_report_by_id(report_id: uuid.UUID) -> Report | None:
    """Get a report by its client-generated id.

    Returns:
        Report | None: The report, or None if it was never submitted.
    """
    return Report.objects.filter(pk=report_id).first()


def get_report_target_snapshot(
    target_type: str, target_id: str
) -> ReportTargetSnapshot | None:
    """Look up the reported item and capture what identifies it.

    Unpublished lessons and courses are found too: an item can be
    unpublished after the user saw it, and the report still applies.

    Args:
        target_type: A content `ReportTargetType` (anything but APP).
        target_id: The id the client knows the item by.

    Returns:
        ReportTargetSnapshot | None: The snapshot, or None if no such item
            exists or the id is malformed for this target type.
    """
    by_uuid: dict[str, QuerySet[Song] | QuerySet[Lesson] | QuerySet[Course]] = {
        ReportTargetType.SONG: Song.objects.all(),
        ReportTargetType.LESSON: Lesson.objects.all(),
        ReportTargetType.COURSE: Course.objects.all(),
    }
    by_pk: dict[str, tuple[QuerySet[Chord] | QuerySet[ImageScheme], str]] = {
        ReportTargetType.CHORD: (Chord.objects.all(), "title"),
        ReportTargetType.SCHEME: (ImageScheme.objects.all(), "code"),
    }

    row: tuple[str, datetime | None] | None = None
    if target_type in by_uuid:
        try:
            key = uuid.UUID(target_id)
        except ValueError:
            return None
        row = (
            by_uuid[target_type]
            .filter(uuid=key)
            .values_list("title", "updated_at")
            .first()
        )
    elif target_type in by_pk and target_id.isdecimal():
        queryset, title_field = by_pk[target_type]
        title = (
            queryset
            .filter(pk=int(target_id))
            .values_list(title_field, flat=True)
            .first()
        )
        row = None if title is None else (title, None)

    if row is None:
        return None
    return ReportTargetSnapshot(title=row[0], updated_at=row[1])
