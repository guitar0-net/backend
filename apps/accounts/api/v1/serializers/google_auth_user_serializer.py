# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the authenticated user payload returned by Google Sign-In."""

from rest_framework import serializers

from apps.accounts.models.user import User


class GoogleAuthUserSerializer(serializers.ModelSerializer[User]):
    """Public profile fields returned alongside the JWT pair."""

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "display_name", "avatar")

    def get_display_name(self, user: User) -> str:  # noqa: PLR6301
        """Return the user's full name, falling back to their email."""
        full_name = user.get_full_name().strip()
        return full_name or user.email
