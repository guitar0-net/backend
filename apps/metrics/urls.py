# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for metrics app."""

from django.urls import path

from .views import metrics_view

app_name = "metrics"

urlpatterns = [
    path("", metrics_view, name="prometheus"),
]
