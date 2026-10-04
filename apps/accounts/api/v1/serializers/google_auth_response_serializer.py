# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the Google Sign-In response payload."""

from typing import TypedDict

from rest_framework import serializers

from apps.accounts.api.v1.serializers.user_profile_serializer import (
    UserProfileSerializer,
)
from apps.accounts.models.user import User


class GoogleAuthPayload(TypedDict):
    """The values GoogleAuthResponseSerializer renders."""

    access: str
    refresh: str
    user: User


class GoogleAuthResponseSerializer(serializers.Serializer[GoogleAuthPayload]):
    """The JWT access/refresh pair and the signed-in user's profile."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserProfileSerializer(read_only=True)
