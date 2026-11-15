# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Custom authentication classes."""

from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import AuthUser, JWTAuthentication
from rest_framework_simplejwt.tokens import Token


class OptionalJWTAuthentication(JWTAuthentication):
    """Identify the caller by JWT when possible, never reject the request.

    simplejwt answers 401 to an expired or otherwise invalid token even on an
    `AllowAny` view. For endpoints where signing in is optional and requests
    may be replayed from an offline queue long after the token expired, the
    request should go through anonymously instead.
    """

    def authenticate(self, request: Request) -> tuple[AuthUser, Token] | None:
        """Return the token's user, or None when the token is unusable."""
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None


class OptionalJWTScheme(SimpleJWTScheme):
    """Document `OptionalJWTAuthentication` as a bearer JWT scheme.

    drf-spectacular's simplejwt extension matches `JWTAuthentication` only,
    not its subclasses, and refuses two classes under one scheme name. The
    extension registers itself on definition, so it lives next to the class
    it describes to be loaded whenever that is.
    """

    target_class = "apps.shared.authentication.OptionalJWTAuthentication"
    name = "optionalJwtAuth"
