# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for lessons API v1."""

from django.urls import path

from .views import LessonDetailView, LessonsListView

urlpatterns = [
    path("lessons/", LessonsListView.as_view(), name="lessons-list"),
    path("lessons/<uuid:uuid>/", LessonDetailView.as_view(), name="lesson-detail"),
]
