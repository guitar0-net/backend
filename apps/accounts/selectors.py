# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the accounts app."""

from apps.accounts.models.social_account import SocialAccount
from apps.accounts.models.user import User


def get_user_by_email(email: str) -> User | None:
    """Get a user by email, case-insensitively.

    Args:
        email: Email address to look up.

    Returns:
        User | None: The matching user, or None if no user has this email.
    """
    return User.objects.filter(email__iexact=email).first()


def get_social_account(provider: str, provider_uid: str) -> SocialAccount | None:
    """Get a social account by provider and provider-issued UID.

    Args:
        provider: Provider name (e.g. "google-oauth2").
        provider_uid: The unique identifier issued by the provider.

    Returns:
        SocialAccount | None: The matching social account, or None if not found.
    """
    return (
        SocialAccount.objects
        .filter(provider=provider, provider_uid=provider_uid)
        .select_related("user")
        .first()
    )
