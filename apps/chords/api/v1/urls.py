# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for chords API v1."""

from django.urls import path

from .views import ChordDetailView, ChordsListView

urlpatterns = [
    path("chords/", ChordsListView.as_view(), name="chords-list"),
    path("chords/<int:pk>/", ChordDetailView.as_view(), name="chord-detail"),
]
