# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializers for the reasons a client may offer per report target type."""

from typing import TypedDict

from rest_framework import serializers


class ReasonPayload(TypedDict):
    """One reason as ReportReasonSerializer renders it."""

    code: str
    title: str
    requires_message: bool


class TargetReasonsPayload(TypedDict):
    """The reasons for one target type as TargetReasonsSerializer renders them."""

    target_type: str
    reasons: list[ReasonPayload]


class ReportReasonSerializer(serializers.Serializer[ReasonPayload]):
    """A reason code, its Russian title and whether a message is mandatory.

    `code` is a plain string rather than an enum: this list exists to reach
    app versions released before a reason was added, and a client generated
    with a closed enum would fail to decode the new code.
    """

    code = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    requires_message = serializers.BooleanField(read_only=True)


class TargetReasonsSerializer(serializers.Serializer[TargetReasonsPayload]):
    """The reasons offered for one target type, in display order.

    `target_type` is a plain string for the same reason as `code`: a client
    skips a target type it has no screen for instead of failing to decode.
    """

    target_type = serializers.CharField(read_only=True)
    reasons = ReportReasonSerializer(many=True, read_only=True)
