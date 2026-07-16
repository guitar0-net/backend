# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""URL configuration for accounts API v1."""

from django.urls import path

from .views import GoogleAuthView, RefreshTokenView, VerifyTokenView

urlpatterns = [
    path("auth/google/", GoogleAuthView.as_view(), name="auth-google"),
    path("auth/token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("auth/token/verify/", VerifyTokenView.as_view(), name="token-verify"),
]
