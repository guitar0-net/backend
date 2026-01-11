# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures for testing songs app."""

import pytest

from apps.songs.models import Song
from apps.songs.tests.factories import SongFactory


@pytest.fixture
def song_factory() -> type[SongFactory]:
    """Fixture providing the SongFactory for creating songs in tests."""
    return SongFactory


@pytest.fixture
def song() -> Song:
    """Fixture creating a song for testing.

    Returns:
        Song: song instance
    """
    return SongFactory.create()
