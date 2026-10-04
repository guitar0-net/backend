# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for rotating a refresh token."""

from typing import Any

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.accounts.models.user import User


class RefreshTokenSerializer(TokenRefreshSerializer):
    """Refuse refresh tokens whose user no longer exists.

    simplejwt looks the user up without catching DoesNotExist, so a token that
    outlives its user would surface as a 500. That happens when the user is
    deleted in the admin, or when a refresh races `delete_account` and its
    rotated token is stored after the blacklisting.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        """Rotate the token, reporting a missing user as an inactive account."""
        try:
            return super().validate(attrs)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed(
                self.error_messages["no_active_account"], "no_active_account"
            ) from exc
