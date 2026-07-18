# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Services for the accounts app."""

from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from google.auth import exceptions as google_auth_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models.social_account import SocialAccount
from apps.accounts.models.user import User
from apps.accounts.selectors import get_social_account, get_user_by_email

GOOGLE_PROVIDER = "google-oauth2"


class InvalidGoogleTokenError(Exception):
    """Raised when a Google ID token fails verification."""


def verify_google_id_token(id_token: str) -> dict[str, Any]:
    """Verify a Google ID token and return its claims.

    Isolated in its own function so tests can stub Google's network call.

    Args:
        id_token: The raw Google ID token from the client.

    Returns:
        dict[str, Any]: The verified token claims.

    Raises:
        InvalidGoogleTokenError: If the token is invalid, expired, or does not
            match the configured Google client ID.
        ImproperlyConfigured: If GOOGLE_CLIENT_ID is not set. Without it, the
            underlying library skips audience validation entirely and would
            accept ID tokens issued to any Google OAuth client.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise ImproperlyConfigured(
            "GOOGLE_CLIENT_ID must be configured to verify Google ID tokens."
        )
    try:
        return google_id_token.verify_oauth2_token(  # type: ignore[no-any-return, no-untyped-call]
            id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except (ValueError, google_auth_exceptions.GoogleAuthError) as exc:
        raise InvalidGoogleTokenError from exc


def authenticate_via_google(id_token: str) -> tuple[User, bool]:
    """Find or create a user from a verified Google ID token.

    Args:
        id_token: The raw Google ID token from the client.

    Returns:
        tuple[User, bool]: The user, and whether it was newly created.

    Raises:
        InvalidGoogleTokenError: If the token is invalid, expired, or its
            email is not verified by Google.
    """
    claims = verify_google_id_token(id_token)
    if not claims.get("email_verified"):
        # An unverified email can't be trusted to look up or create an
        # account, since it may not actually belong to the token holder.
        raise InvalidGoogleTokenError
    sub = claims["sub"]
    email = claims["email"]

    social_account = get_social_account(GOOGLE_PROVIDER, sub)
    if social_account is not None:
        return social_account.user, False

    try:
        with transaction.atomic():
            user = get_user_by_email(email)
            created = False
            if user is None:
                user = User.objects.create_user(
                    email=email,
                    password=None,
                    first_name=claims.get("given_name", ""),
                    last_name=claims.get("family_name", ""),
                    avatar=claims.get("picture", ""),
                )
                created = True

            SocialAccount.objects.create(
                user=user,
                provider=GOOGLE_PROVIDER,
                provider_uid=sub,
                extra_data=claims,
            )
    except IntegrityError:
        # Lost a race with a concurrent request for the same Google identity
        # (unique provider_uid) or the same new user's email (unique email).
        # Whichever request won committed both rows together, so it is always
        # findable by provider/uid at this point.
        social_account = get_social_account(GOOGLE_PROVIDER, sub)
        if social_account is None:
            raise
        return social_account.user, False

    return user, created


def blacklist_refresh_token(token: str) -> None:
    """Blacklist a refresh token so it can no longer be used to refresh or log out.

    Args:
        token: The raw refresh token to invalidate.

    Raises:
        InvalidToken: If the token is malformed, expired, or already blacklisted.
    """
    try:
        # simplejwt's own annotation for `token` is `Token | None`, but the
        # constructor actually decodes a raw encoded token string.
        RefreshToken(token).blacklist()  # type: ignore[arg-type]
    except TokenError as exc:
        raise InvalidToken from exc
