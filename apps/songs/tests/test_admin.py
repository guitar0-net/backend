# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs admin."""

from datetime import UTC, datetime

import pytest
from django.contrib.admin.sites import AdminSite
from django.forms.models import modelform_factory
from django.test import Client, RequestFactory
from django.urls import reverse

from apps.chords.tests.factories import ChordFactory
from apps.lessons.models import Lesson
from apps.lessons.tests.factories import LessonFactory
from apps.songs.admin import SongAdmin, SongAdminForm
from apps.songs.models import Song
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_song_admin_save_model_propagates_updated_at_to_related_lessons() -> None:
    old_ts = datetime(2026, 1, 1, tzinfo=UTC)
    song = SongFactory.create()
    lesson = LessonFactory.create(songs=[song], updated_at=old_ts)
    form = modelform_factory(Song, fields=("title",))(instance=song)

    SongAdmin(Song, AdminSite()).save_model(
        request=RequestFactory().post("/"), obj=song, form=form, change=False
    )

    lesson.refresh_from_db()
    assert lesson.updated_at > old_ts


@pytest.mark.django_db
def test_song_admin_delete_model_propagates_updated_at_to_related_lessons() -> None:
    stale = datetime(2026, 6, 5, tzinfo=UTC)
    song = SongFactory.create(title="Остання електричка")
    lesson = LessonFactory.create(songs=[song])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    SongAdmin(Song, AdminSite()).delete_model(RequestFactory().post("/"), song)

    lesson.refresh_from_db()
    assert lesson.updated_at > stale


@pytest.mark.django_db
def test_song_admin_delete_queryset_propagates_updated_at_to_related_lessons() -> None:
    stale = datetime(2026, 6, 6, tzinfo=UTC)
    lesson = LessonFactory.create(songs=[SongFactory.create(title="Гроза в степу")])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    SongAdmin(Song, AdminSite()).delete_queryset(
        RequestFactory().post("/"), Song.objects.all()
    )

    lesson.refresh_from_db()
    assert lesson.updated_at > stale


def _song_form_data(**fields: object) -> dict[str, object]:
    return {"title": "Город золотой", "metronome": 96, "text": "", "chord_text": ""} | (
        fields
    )


def test_song_admin_form_rejects_unclosed_chord_bracket() -> None:
    form = SongAdminForm(data=_song_form_data(chord_text="Под [Am небом голубым"))

    assert not form.is_valid()


def test_song_admin_form_rejects_song_without_any_text() -> None:
    form = SongAdminForm(data=_song_form_data())

    assert not form.is_valid()


@pytest.mark.django_db
def test_song_admin_form_accepts_song_with_only_chord_text() -> None:
    form = SongAdminForm(data=_song_form_data(chord_text="Под [Am]небом [E]голубым"))

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_song_admin_change_of_chord_text_propagates_updated_at_to_lessons(
    admin_client: Client,
) -> None:
    stale = datetime(2026, 3, 8, tzinfo=UTC)
    song = SongFactory.create(title="Есть город золотой")
    lesson = LessonFactory.create(songs=[song])
    Lesson.objects.filter(pk=lesson.pk).update(updated_at=stale)

    admin_client.post(
        reverse("admin:songs_song_change", args=[song.pk]),
        _song_form_data(title=song.title, chord_text="Под [Am]небом голубым"),
    )

    lesson.refresh_from_db()
    assert lesson.updated_at > stale


@pytest.mark.django_db
def test_song_admin_warns_about_chords_missing_from_song(admin_client: Client) -> None:
    chord = ChordFactory.create(title="Am")

    response = admin_client.post(
        reverse("admin:songs_song_add"),
        _song_form_data(chord_text="Под [Am]небом [Fm#(8)]голубым", chords=[chord.pk]),
        follow=True,
    )

    assert any("Fm#" in str(m) for m in response.context["messages"])
