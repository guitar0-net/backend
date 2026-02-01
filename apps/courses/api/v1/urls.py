# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for courses API v1."""

from django.urls import path

from .views import CourseDetailView, CoursesListView

urlpatterns = [
    path("courses/", CoursesListView.as_view(), name="courses-list"),
    path("courses/<uuid:uuid>/", CourseDetailView.as_view(), name="course-detail"),
]
