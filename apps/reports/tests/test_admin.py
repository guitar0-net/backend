# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports admin."""

import pytest
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse

from apps.reports.admin import ReportAdmin
from apps.reports.constants import ReportStatus
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
