# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for accounts API v1."""

from django.urls import path

from .views import GoogleAuthView

urlpatterns = [
    path("auth/google/", GoogleAuthView.as_view(), name="auth-google"),
]
