# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs admin."""

from datetime import UTC, datetime

import pytest
from django.contrib.admin.sites import AdminSite

from apps.lessons.tests.factories import LessonFactory
from apps.songs.admin import SongAdmin
from apps.songs.models import Song
from apps.songs.tests.factories import SongFactory


@pytest.mark.django_db
def test_song_admin_save_model_propagates_updated_at_to_related_lessons() -> None:
    old_ts = datetime(2026, 1, 1, tzinfo=UTC)
    song = SongFactory.create()
    lesson = LessonFactory.create(songs=[song], updated_at=old_ts)

    SongAdmin(Song, AdminSite()).save_model(
        request=object(), obj=song, form=object(), change=False
    )

    lesson.refresh_from_db()
    assert lesson.updated_at > old_ts
