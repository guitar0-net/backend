# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializer for the report submission response."""

from rest_framework import serializers

from apps.reports.models import Report


class ReportSerializer(serializers.ModelSerializer[Report]):
    """Acknowledge a report without echoing what was submitted.

    A resubmitted id returns the stored report, so echoing the message or
    contact email would hand them to anyone who learned the id.
    """

    class Meta:
        """Metadata for ReportSerializer."""

        model = Report
        fields = ("id", "status", "created_at")
        read_only_fields = fields
