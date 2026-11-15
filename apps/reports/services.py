# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Services for the reports app: accepting reports and processing them."""

import uuid
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models.user import User
from apps.reports.constants import ReportTargetType
from apps.reports.metrics import reports_submitted_total
from apps.reports.models import Report
from apps.reports.selectors import get_report_by_id, get_report_target_snapshot


class UnknownReportTargetError(Exception):
    """Raised when the reported content item does not exist.

    Retrying will not help, so the client should drop the queued report.
    """


@dataclass(frozen=True, kw_only=True)
class ReportSubmission:
    """A report as the client sent it, already validated."""

    id: uuid.UUID
    target_type: str
    target_id: str
    reason: str
    message: str
    contact_email: str
    device_id: str
    platform: str
    app_version: str
    os_version: str
    locale: str
    screen: str


def submit_report(
    submission: ReportSubmission, *, user: User | None
) -> tuple[Report, bool]:
    """Record a report, or return the one already recorded under its id.

    A known id short-circuits before the target lookup, so a queued report
    whose target was deleted meanwhile is still acknowledged on retry.

    Returns:
        tuple[Report, bool]: The report, and whether it was created now.

    Raises:
        UnknownReportTargetError: The content item being reported is unknown.
    """
    existing = get_report_by_id(submission.id)
    if existing is not None:
        return existing, False

    title, target_updated_at = "", None
    if submission.target_type != ReportTargetType.APP:
        snapshot = get_report_target_snapshot(
            submission.target_type, submission.target_id
        )
        if snapshot is None:
            raise UnknownReportTargetError(
                f"No {submission.target_type} with id {submission.target_id!r}"
            )
        title, target_updated_at = snapshot.title, snapshot.updated_at

    try:
        with transaction.atomic():
            report = Report.objects.create(
                id=submission.id,
                target_type=submission.target_type,
                target_id=submission.target_id,
                target_title=title,
                target_updated_at=target_updated_at,
                reason=submission.reason,
                message=submission.message,
                contact_email=submission.contact_email,
                user=user,
                device_id=submission.device_id,
                platform=submission.platform,
                app_version=submission.app_version,
                os_version=submission.os_version,
                locale=submission.locale,
                screen=submission.screen,
            )
    except IntegrityError:
        concurrent = get_report_by_id(submission.id)
        if concurrent is None:
            raise
        return concurrent, False

    reports_submitted_total.labels(
        target_type=submission.target_type, reason=submission.reason
    ).inc()
    return report, True


def set_reports_status(reports: QuerySet[Report], status: str) -> int:
    """Move reports to a new processing status.

    Returns:
        int: How many reports were updated.
    """
    return reports.update(status=status, updated_at=timezone.now())
