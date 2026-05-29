# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for sync API v1."""

from django.urls import path

from .views import ContentVersionView, LessonsSyncView

urlpatterns = [
    path("sync/lessons/", LessonsSyncView.as_view(), name="sync-lessons"),
    path("sync/version/", ContentVersionView.as_view(), name="sync-version"),
]
