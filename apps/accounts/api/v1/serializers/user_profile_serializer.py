# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for a user's public profile fields."""

from rest_framework import serializers

from apps.accounts.models.user import User


class UserProfileSerializer(serializers.ModelSerializer[User]):
    """Public profile fields shared by the auth and profile endpoints."""

    class Meta:
        model = User
        fields = ("email", "display_name", "avatar")
