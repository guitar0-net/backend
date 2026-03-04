# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for announcements API v1."""

from django.urls import path

from .views import AnnouncementDetailView, AnnouncementsListView

urlpatterns = [
    path("announcements/", AnnouncementsListView.as_view(), name="announcements-list"),
    path(
        "announcements/<uuid:uuid>/",
        AnnouncementDetailView.as_view(),
        name="announcement-detail",
    ),
]
