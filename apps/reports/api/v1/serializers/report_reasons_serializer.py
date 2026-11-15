# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializers for the reasons a client may offer per report target type."""

from typing import TypedDict

from rest_framework import serializers

from apps.reports.constants import ReportReason, ReportTargetType


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
    """A reason code, its Russian title and whether a message is mandatory."""

    code = serializers.ChoiceField(choices=ReportReason.choices, read_only=True)
    title = serializers.CharField(read_only=True)
    requires_message = serializers.BooleanField(read_only=True)


class TargetReasonsSerializer(serializers.Serializer[TargetReasonsPayload]):
    """The reasons offered for one target type, in display order."""

    target_type = serializers.ChoiceField(
        choices=ReportTargetType.choices, read_only=True
    )
    reasons = ReportReasonSerializer(many=True, read_only=True)
