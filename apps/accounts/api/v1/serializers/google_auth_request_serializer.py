# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the Google Sign-In request payload."""

from rest_framework import serializers


class GoogleAuthRequestSerializer(serializers.Serializer[None]):
    """Validates the incoming Google ID token."""

    id_token = serializers.CharField()
