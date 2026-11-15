# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for reports API v1."""

from django.urls import path

from .views import ReportCreateView, ReportReasonsView

urlpatterns = [
    path("reports/", ReportCreateView.as_view(), name="report-create"),
    path("reports/reasons/", ReportReasonsView.as_view(), name="report-reasons"),
]
