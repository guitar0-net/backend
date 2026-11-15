# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports admin."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse
from faker import Faker

from apps.reports.admin import ReportAdmin
from apps.reports.constants import ReportStatus, ReportTargetType
from apps.reports.models import Report
from apps.reports.tests.factories import ReportFactory


def test_report_admin_forbids_adding_reports_by_hand() -> None:
    can_add = ReportAdmin(Report, AdminSite()).has_add_permission(HttpRequest())

    assert can_add is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("action", "expected"),
    [
        ("mark_in_progress", ReportStatus.IN_PROGRESS),
        ("mark_resolved", ReportStatus.RESOLVED),
        ("mark_rejected", ReportStatus.REJECTED),
    ],
)
def test_report_admin_action_moves_selected_reports_to_its_status(
    admin_client: Client, action: str, expected: ReportStatus
) -> None:
    report = ReportFactory.create(status=ReportStatus.NEW)

    admin_client.post(
        reverse("admin:reports_report_changelist"),
        {"action": action, "_selected_action": [str(report.pk)]},
    )

    report.refresh_from_db()
    assert report.status == expected


@pytest.mark.django_db
def test_report_admin_lets_staff_change_the_status_from_the_form(
    admin_client: Client,
) -> None:
    report = ReportFactory.create(status=ReportStatus.NEW)

    admin_client.post(
        reverse("admin:reports_report_change", args=[report.pk]),
        {"status": ReportStatus.RESOLVED, "staff_note": "Исправил аккорды"},
    )

    report.refresh_from_db()
    assert report.status == ReportStatus.RESOLVED


def _outdated(target_type: str, version: datetime, edited: datetime) -> bool | None:
    report = ReportFactory.build(
        target_type=target_type,
        target_id=str(uuid.uuid4()),
        content_version=version,
        target_updated_at=edited,
    )
    return ReportAdmin(Report, AdminSite()).client_content_outdated(report)


def test_report_admin_flags_a_song_edited_after_the_client_synced(
    fake: Faker,
) -> None:
    synced = fake.date_time(tzinfo=UTC)

    outdated = _outdated(
        ReportTargetType.SONG, synced, synced + timedelta(minutes=fake.pyint(1))
    )

    assert outdated is True


def test_report_admin_does_not_flag_a_song_the_client_already_had(
    fake: Faker,
) -> None:
    edited = fake.date_time(tzinfo=UTC)

    outdated = _outdated(
        ReportTargetType.LESSON, edited + timedelta(minutes=fake.pyint(1)), edited
    )

    assert outdated is False


def test_report_admin_cannot_tell_staleness_for_a_course(fake: Faker) -> None:
    synced = fake.date_time(tzinfo=UTC)

    outdated = _outdated(
        ReportTargetType.COURSE, synced, synced + timedelta(minutes=fake.pyint(1))
    )

    assert outdated is None


def test_report_admin_cannot_tell_staleness_without_a_client_version() -> None:
    report = ReportFactory.build(
        target_type=ReportTargetType.SONG,
        target_id=str(uuid.uuid4()),
        target_updated_at=datetime.now(UTC),
    )

    outdated = ReportAdmin(Report, AdminSite()).client_content_outdated(report)

    assert outdated is None
