# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for songs API v1."""

from django.urls import path

from .views import SongPrintView

urlpatterns = [
    path("songs/<uuid:uuid>/print/", SongPrintView.as_view(), name="song-print"),
]
