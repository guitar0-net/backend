# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports services."""

import dataclasses
import uuid
from collections.abc import Iterator
from datetime import UTC

import pytest
from faker import Faker

from apps.accounts.tests.factories.user import UserFactory
from apps.ops.registry import get_registry
from apps.reports.constants import ReportReason, ReportStatus, ReportTargetType
from apps.reports.models import Report
from apps.reports.selectors import get_report_by_id
from apps.reports.services import (
    ReportSubmission,
    UnknownReportTargetError,
    set_reports_status,
    submit_report,
)
from apps.reports.tests.factories import ReportFactory
from apps.songs.tests.factories import SongFactory


def _song_submission(base: ReportSubmission, song_uuid: uuid.UUID) -> ReportSubmission:
    return dataclasses.replace(
        base,
        target_type=ReportTargetType.SONG,
        target_id=str(song_uuid),
        reason=ReportReason.WRONG_CHORDS,
    )


@pytest.mark.django_db
def test_submit_report_creates_a_new_report(app_submission: ReportSubmission) -> None:
    _report, created = submit_report(app_submission, user=None)

    assert created is True


@pytest.mark.django_db
def test_submit_report_stores_the_client_generated_id(
    app_submission: ReportSubmission,
) -> None:
    report, _created = submit_report(app_submission, user=None)

    assert report.pk == app_submission.id


@pytest.mark.django_db
def test_submit_report_remembers_the_song_title(
    app_submission: ReportSubmission, fake: Faker
) -> None:
    song = SongFactory.create(title=fake.sentence())

    report, _created = submit_report(
        _song_submission(app_submission, song.uuid), user=None
    )

    assert report.target_title == song.title


@pytest.mark.django_db
def test_submit_report_stores_the_content_version_the_client_had(
    app_submission: ReportSubmission, fake: Faker
) -> None:
    version = fake.date_time(tzinfo=UTC)

    report, _created = submit_report(
        dataclasses.replace(app_submission, content_version=version), user=None
    )

    assert report.content_version == version


@pytest.mark.django_db
def test_submit_report_attaches_the_signed_in_user(
    app_submission: ReportSubmission, fake: Faker
) -> None:
    user = UserFactory.create(email=fake.email())

    report, _created = submit_report(app_submission, user=user)

    assert report.user == user


@pytest.mark.django_db
def test_submit_report_does_not_create_a_second_report_on_resubmission(
    app_submission: ReportSubmission,
) -> None:
    submit_report(app_submission, user=None)

    _report, created = submit_report(app_submission, user=None)

    assert created is False


@pytest.mark.django_db
def test_submit_report_keeps_the_original_message_on_resubmission(
    app_submission: ReportSubmission, fake: Faker
) -> None:
    submit_report(app_submission, user=None)

    report, _created = submit_report(
        dataclasses.replace(app_submission, message=fake.sentence()), user=None
    )

    assert report.message == app_submission.message


@pytest.mark.django_db
def test_submit_report_rejects_a_song_that_does_not_exist(
    app_submission: ReportSubmission,
) -> None:
    with pytest.raises(UnknownReportTargetError):
        submit_report(_song_submission(app_submission, uuid.uuid4()), user=None)


@pytest.mark.django_db
def test_submit_report_acknowledges_a_resubmission_after_the_song_was_deleted(
    app_submission: ReportSubmission, fake: Faker
) -> None:
    song = SongFactory.create(title=fake.sentence())
    submission = _song_submission(app_submission, song.uuid)
    submit_report(submission, user=None)
    song.delete()

    report, _created = submit_report(submission, user=None)

    assert report.pk == submission.id


@pytest.mark.django_db
def test_submit_report_returns_the_report_a_concurrent_request_created_first(
    app_submission: ReportSubmission, monkeypatch: pytest.MonkeyPatch
) -> None:
    ReportFactory.create(id=app_submission.id)
    lookups: Iterator[Report | None] = iter([None, get_report_by_id(app_submission.id)])
    monkeypatch.setattr(
        "apps.reports.services.get_report_by_id", lambda _report_id: next(lookups)
    )

    _report, created = submit_report(app_submission, user=None)

    assert created is False


@pytest.mark.django_db
def test_submit_report_counts_accepted_reports_for_alerting(
    app_submission: ReportSubmission,
) -> None:
    labels = {
        "target_type": app_submission.target_type,
        "reason": app_submission.reason,
    }
    metric = "guitar0_backend_reports_submitted_total"
    before = get_registry().get_sample_value(metric, labels) or 0.0

    submit_report(app_submission, user=None)

    assert get_registry().get_sample_value(metric, labels) == before + 1


@pytest.mark.django_db
def test_set_reports_status_moves_reports_to_the_given_status() -> None:
    report = ReportFactory.create(status=ReportStatus.NEW)

    set_reports_status(Report.objects.filter(pk=report.pk), ReportStatus.RESOLVED)

    report.refresh_from_db()
    assert report.status == ReportStatus.RESOLVED


@pytest.mark.django_db
def test_set_reports_status_reports_how_many_reports_changed() -> None:
    reports = ReportFactory.create_batch(3, status=ReportStatus.NEW)

    updated = set_reports_status(
        Report.objects.filter(pk__in=[r.pk for r in reports]), ReportStatus.REJECTED
    )

    assert updated == len(reports)
