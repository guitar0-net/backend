# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the claim-device response payload."""

from typing import TypedDict

from rest_framework import serializers


class ClaimDevicePayload(TypedDict):
    """The values ClaimDeviceResponseSerializer renders."""

    claimed: int


class ClaimDeviceResponseSerializer(serializers.Serializer[ClaimDevicePayload]):
    """How many anonymous purchases were attached to the user."""

    claimed = serializers.IntegerField(read_only=True)
