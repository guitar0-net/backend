# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factory for generating test SocialAccount instances."""

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models.social_account import SocialAccount
from apps.accounts.tests.factories.user import UserFactory


class SocialAccountFactory(DjangoModelFactory[SocialAccount]):
    """Factory for creating SocialAccount instances."""

    class Meta:
        """Metadata for SocialAccountFactory."""

        model = SocialAccount

    user = factory.SubFactory(UserFactory)
    provider = "google-oauth2"
    provider_uid = factory.Sequence(lambda n: f"uid-{n}")
    extra_data = factory.LazyFunction(dict)
