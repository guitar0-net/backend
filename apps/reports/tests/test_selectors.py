# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports selectors."""

import uuid

import pytest
from faker import Faker

from apps.chords.tests.factories import ChordFactory
from apps.courses.tests.factories import CourseFactory
from apps.lessons.tests.factories import LessonFactory
from apps.reports.constants import ReportTargetType
from apps.reports.selectors import get_report_by_id, get_report_target_snapshot
from apps.reports.tests.factories import ReportFactory
from apps.schemes.tests.factories import ImageSchemeFactory
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_get_report_by_id_finds_a_submitted_report() -> None:
    report = ReportFactory.create()

    assert get_report_by_id(report.pk) == report


@pytest.mark.django_db
def test_get_report_by_id_returns_none_for_an_unknown_id() -> None:
    assert get_report_by_id(uuid.uuid4()) is None


@pytest.mark.django_db
def test_target_snapshot_captures_the_song_title(fake: Faker) -> None:
    song = SongFactory.create(title=fake.sentence())

    snapshot = get_report_target_snapshot(ReportTargetType.SONG, str(song.uuid))

    assert snapshot is not None and snapshot.title == song.title


@pytest.mark.django_db
def test_target_snapshot_captures_when_the_lesson_was_last_updated(
    fake: Faker,
) -> None:
    lesson = LessonFactory.create(title=fake.sentence())

    snapshot = get_report_target_snapshot(ReportTargetType.LESSON, str(lesson.uuid))

    assert snapshot is not None and snapshot.updated_at == lesson.updated_at


@pytest.mark.django_db
def test_target_snapshot_finds_an_unpublished_course(fake: Faker) -> None:
    course = CourseFactory.create(title=fake.sentence(), is_published=False)

    snapshot = get_report_target_snapshot(ReportTargetType.COURSE, str(course.uuid))

    assert snapshot is not None and snapshot.title == course.title


@pytest.mark.django_db
def test_target_snapshot_captures_the_chord_title(fake: Faker) -> None:
    chord = ChordFactory.create(title=fake.lexify("??"))

    snapshot = get_report_target_snapshot(ReportTargetType.CHORD, str(chord.pk))

    assert snapshot is not None and snapshot.title == chord.title


@pytest.mark.django_db
@pytest.mark.usefixtures("media_root")
def test_target_snapshot_identifies_a_scheme_by_its_code(fake: Faker) -> None:
    scheme = ImageSchemeFactory.create(code=fake.lexify("схема-????"))

    snapshot = get_report_target_snapshot(ReportTargetType.SCHEME, str(scheme.pk))

    assert snapshot is not None and snapshot.title == scheme.code


@pytest.mark.django_db
def test_target_snapshot_returns_none_for_an_unknown_song() -> None:
    assert get_report_target_snapshot(ReportTargetType.SONG, str(uuid.uuid4())) is None


@pytest.mark.django_db
def test_target_snapshot_returns_none_for_a_malformed_song_id(fake: Faker) -> None:
    assert get_report_target_snapshot(ReportTargetType.SONG, fake.word()) is None


@pytest.mark.django_db
def test_target_snapshot_returns_none_for_a_non_numeric_chord_id(
    fake: Faker,
) -> None:
    assert get_report_target_snapshot(ReportTargetType.CHORD, fake.word()) is None


@pytest.mark.django_db
def test_target_snapshot_returns_none_for_the_app_itself(fake: Faker) -> None:
    assert get_report_target_snapshot(ReportTargetType.APP, fake.word()) is None
