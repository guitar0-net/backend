# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs services."""

import hashlib
import uuid
from datetime import UTC, datetime

import pytest

from apps.chords.tests.factories import ChordFactory
from apps.lessons.models import Lesson
from apps.lessons.tests.factories import LessonFactory
from apps.songs.models import Song
from apps.songs.services import (
    ChordTextImport,
    delete_song,
    delete_songs,
    import_chord_texts,
    save_song,
)
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_save_song_persists_changes_to_the_database() -> None:
    song = SongFactory.create()
    song.title = "Обновлённое название"

    save_song(song)

    song.refresh_from_db()
    assert song.title == "Обновлённое название"


@pytest.mark.django_db
def test_save_song_propagates_updated_at_to_related_lessons() -> None:
    old_ts = datetime(2026, 1, 1, tzinfo=UTC)
    song = SongFactory.create()
    lesson = LessonFactory.create(songs=[song])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=old_ts)

    save_song(song)

    lesson.refresh_from_db()
    assert lesson.updated_at > old_ts


@pytest.mark.django_db
def test_save_song_does_not_affect_unrelated_lessons() -> None:
    old_ts = datetime(2026, 1, 1, tzinfo=UTC)
    song = SongFactory.create()
    unrelated = LessonFactory.create()
    Lesson.objects.filter(pk=unrelated.pk).update(updated_at=old_ts)

    save_song(song)

    unrelated.refresh_from_db()
    assert unrelated.updated_at == old_ts


@pytest.mark.django_db
def test_delete_song_stamps_lessons_before_the_relation_disappears() -> None:
    stale = datetime(2026, 1, 2, tzinfo=UTC)
    song = SongFactory.create(title="Стежка до моря")
    lesson = LessonFactory.create(songs=[song])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    delete_song(song)

    lesson.refresh_from_db()
    assert lesson.updated_at > stale


@pytest.mark.django_db
def test_delete_songs_stamps_lessons_before_the_relation_disappears() -> None:
    stale = datetime(2026, 1, 3, tzinfo=UTC)
    lesson = LessonFactory.create(songs=[SongFactory.create(title="Зорі над Дністром")])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    delete_songs(Song.objects.all())

    lesson.refresh_from_db()
    assert lesson.updated_at > stale


def _conversion_of(song: Song, chord_text: str) -> ChordTextImport:
    return ChordTextImport(
        song.uuid, hashlib.sha256(song.text.encode()).hexdigest(), chord_text
    )


@pytest.mark.django_db
def test_import_chord_texts_fills_chord_text_of_matching_song() -> None:
    song = SongFactory.create(text="Белый снег, серый лёд")

    import_chord_texts(
        [_conversion_of(song, "[Am]Белый снег, серый лёд")],
        overwrite=False,
        dry_run=False,
    )

    song.refresh_from_db()
    assert song.chord_text == "[Am]Белый снег, серый лёд"


@pytest.mark.django_db
def test_import_chord_texts_propagates_updated_at_to_related_lessons() -> None:
    stale = datetime(2026, 2, 14, tzinfo=UTC)
    song = SongFactory.create(text="Город в дорожной петле")
    lesson = LessonFactory.create(songs=[song])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    import_chord_texts(
        [_conversion_of(song, "Город в [G(4)]дорожной петле")],
        overwrite=False,
        dry_run=False,
    )

    lesson.refresh_from_db()
    assert lesson.updated_at > stale


@pytest.mark.django_db
def test_import_chord_texts_bumps_updated_at_of_the_song() -> None:
    stale = datetime(2026, 2, 15, tzinfo=UTC)
    song = SongFactory.create(text="Прожитых под светом звезды")
    Song.objects.filter(pk=song.pk).update(updated_at=stale)

    import_chord_texts(
        [_conversion_of(song, "[Dm(4)]Прожитых под светом звезды")],
        overwrite=False,
        dry_run=False,
    )

    song.refresh_from_db()
    assert song.updated_at > stale


@pytest.mark.django_db
def test_import_chord_texts_accepts_uppercase_source_hash() -> None:
    song = SongFactory.create(text="По имени Солнце")
    digest = hashlib.sha256(song.text.encode()).hexdigest().upper()

    report = import_chord_texts(
        [ChordTextImport(song.uuid, digest, "По имени [Am]Солнце")],
        overwrite=False,
        dry_run=False,
    )

    assert report.updated == [song.uuid]


@pytest.mark.django_db
def test_import_chord_texts_skips_song_whose_text_changed_after_snapshot() -> None:
    song = SongFactory.create(text="Две тысячи лет — война")
    conversion = _conversion_of(song, "[Am]Две тысячи лет — война")
    Song.objects.filter(pk=song.pk).update(text="Война без особых причин")

    report = import_chord_texts([conversion], overwrite=False, dry_run=False)

    assert report.stale == [song.uuid]


@pytest.mark.django_db
def test_import_chord_texts_leaves_stale_song_unchanged() -> None:
    song = SongFactory.create(text="Война — дело молодых")
    conversion = _conversion_of(song, "[Am]Война — дело молодых")
    Song.objects.filter(pk=song.pk).update(text="Лекарство против морщин")

    import_chord_texts([conversion], overwrite=False, dry_run=False)

    song.refresh_from_db()
    assert not song.chord_text


@pytest.mark.django_db
def test_import_chord_texts_reports_unknown_uuid() -> None:
    missing = uuid.uuid4()

    report = import_chord_texts(
        [ChordTextImport(missing, hashlib.sha256(b"x").hexdigest(), "[C]Ля")],
        overwrite=False,
        dry_run=False,
    )

    assert report.unknown == [missing]


@pytest.mark.django_db
def test_import_chord_texts_keeps_filled_chord_text_without_overwrite() -> None:
    song = SongFactory.create(text="Красная-красная кровь", chord_text="[Am]Ручная")

    import_chord_texts(
        [_conversion_of(song, "[Hm]Красная-красная кровь")],
        overwrite=False,
        dry_run=False,
    )

    song.refresh_from_db()
    assert song.chord_text == "[Am]Ручная"


@pytest.mark.django_db
def test_import_chord_texts_reports_filled_song_without_overwrite() -> None:
    song = SongFactory.create(text="Через час уже просто земля", chord_text="[C]Да")

    report = import_chord_texts(
        [_conversion_of(song, "[C]Через час уже просто земля")],
        overwrite=False,
        dry_run=False,
    )

    assert report.already_filled == [song.uuid]


@pytest.mark.django_db
def test_import_chord_texts_replaces_filled_chord_text_with_overwrite() -> None:
    song = SongFactory.create(text="Через два на ней цветы и трава", chord_text="[C]")

    import_chord_texts(
        [_conversion_of(song, "Через [Em]два на ней цветы")],
        overwrite=True,
        dry_run=False,
    )

    song.refresh_from_db()
    assert song.chord_text == "Через [Em]два на ней цветы"


@pytest.mark.django_db
def test_import_chord_texts_writes_nothing_on_dry_run() -> None:
    song = SongFactory.create(text="Через три она снова жива")

    import_chord_texts(
        [_conversion_of(song, "Через [G]три она снова жива")],
        overwrite=False,
        dry_run=True,
    )

    song.refresh_from_db()
    assert not song.chord_text


@pytest.mark.django_db
def test_import_chord_texts_leaves_lessons_untouched_on_dry_run() -> None:
    stale = datetime(2026, 2, 16, tzinfo=UTC)
    song = SongFactory.create(text="И согрета лучами звезды")
    lesson = LessonFactory.create(songs=[song])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    import_chord_texts(
        [_conversion_of(song, "И [Hm]согрета лучами звезды")],
        overwrite=False,
        dry_run=True,
    )

    lesson.refresh_from_db()
    assert lesson.updated_at == stale


@pytest.mark.django_db
def test_import_chord_texts_skips_malformed_chord_brackets() -> None:
    song = SongFactory.create(text="Группа крови на рукаве")

    report = import_chord_texts(
        [_conversion_of(song, "Группа [Am крови на рукаве")],
        overwrite=False,
        dry_run=False,
    )

    assert song.uuid in report.invalid


@pytest.mark.django_db
def test_import_chord_texts_reports_chords_missing_from_song() -> None:
    song = SongFactory.create(
        text="Мой порядковый номер", chords=[ChordFactory.create(title="Am")]
    )

    report = import_chord_texts(
        [_conversion_of(song, "[Am]Мой порядковый [Fm#(8)]номер")],
        overwrite=False,
        dry_run=False,
    )

    assert report.unknown_chords == {song.uuid: {"Fm#"}}
