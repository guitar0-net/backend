# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the accounts app."""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.accounts.models.user import User
from apps.accounts.services import (
    InvalidGoogleTokenError,
    authenticate_via_google,
    blacklist_refresh_token,
)

from .serializers.google_auth_request_serializer import GoogleAuthRequestSerializer
from .serializers.logout_request_serializer import LogoutRequestSerializer
from .serializers.user_profile_serializer import UserProfileSerializer

logger = logging.getLogger("accounts")


class GoogleAuthView(APIView):
    """Exchange a Google ID token for a JWT access/refresh pair."""

    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:  # noqa: PLR6301
        """Verify the Google ID token and return JWT tokens for the user."""
        request_serializer = GoogleAuthRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            user, _created = authenticate_via_google(
                request_serializer.validated_data["id_token"]
            )
        except InvalidGoogleTokenError:
            logger.info("Rejected invalid Google ID token")
            return Response({"detail": "Invalid or expired Google token."}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data,
        })


class RefreshTokenView(TokenRefreshView):
    """Rotate a refresh token for a new access/refresh pair."""


class VerifyTokenView(TokenVerifyView):
    """Verify that a JWT access token is valid."""


class MeView(APIView):
    """Return the authenticated user's own profile."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:  # noqa: PLR6301
        """Return the requesting user's profile fields."""
        # IsAuthenticated has already run by this point, so request.user is
        # a real User, never AnonymousUser.
        assert isinstance(request.user, User)
        return Response(UserProfileSerializer(request.user).data)


class LogoutView(APIView):
    """Blacklist a refresh token, ending the associated session."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:  # noqa: PLR6301
        """Blacklist the given refresh token."""
        serializer = LogoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blacklist_refresh_token(serializer.validated_data["refresh"])
        return Response(status=status.HTTP_204_NO_CONTENT)
