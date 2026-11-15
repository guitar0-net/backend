# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin settings for the reports app."""

from typing import ClassVar

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.reports.constants import CONTENT_VERSIONED_TARGET_TYPES, ReportStatus
from apps.reports.models import Report
from apps.reports.services import set_reports_status


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Admin interface for the Report model.

    What the user submitted is read-only; staff only move the report through
    its statuses and keep a note. Deleting stays allowed so a user's request
    to erase their data can be honoured.
    """

    list_display = (
        "created_at",
        "target_type",
        "target_title",
        "client_content_outdated",
        "reason",
        "status",
        "platform",
        "app_version",
        "contact_email",
    )
    list_filter = ("status", "target_type", "target_missing", "reason", "platform")
    search_fields = (
        "target_id",
        "target_title",
        "message",
        "contact_email",
        "device_id",
        "user__email",
    )
    date_hierarchy = "created_at"
    fields = (
        "status",
        "staff_note",
        "target_type",
        "target_id",
        "target_title",
        "target_updated_at",
        "target_missing",
        "content_version",
        "client_content_outdated",
        "reason",
        "message",
        "contact_email",
        "user",
        "device_id",
        "platform",
        "app_version",
        "os_version",
        "locale",
        "screen",
        "id",
        "created_at",
        "updated_at",
    )
    readonly_fields: ClassVar[tuple[str, ...]] = tuple(
        field for field in fields if field not in {"status", "staff_note"}
    )
    actions = ("mark_in_progress", "mark_resolved", "mark_rejected")

    @admin.display(description="У клиента старая версия", boolean=True)
    def client_content_outdated(self, report: Report) -> bool | None:  # noqa: PLR6301
        """Tell whether the item was edited after the client last synced.

        Such a report may already be fixed and can be closed. None means it
        cannot be told: the client sent no version, or the target type does
        not move the sync version.
        """
        if (
            report.target_type not in CONTENT_VERSIONED_TARGET_TYPES
            or report.content_version is None
            or report.target_updated_at is None
        ):
            return None
        return report.content_version < report.target_updated_at

    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa: PLR6301
        """Disallow creating reports by hand; they come from users only."""
        return False

    def _set_status(
        self, request: HttpRequest, queryset: QuerySet[Report], status: str
    ) -> None:
        updated = set_reports_status(queryset, status)
        self.message_user(
            request, f"Обновлено отчётов: {updated}", level=messages.SUCCESS
        )

    @admin.action(description="Взять в работу")
    def mark_in_progress(
        self, request: HttpRequest, queryset: QuerySet[Report]
    ) -> None:
        """Move the selected reports to IN_PROGRESS."""
        self._set_status(request, queryset, ReportStatus.IN_PROGRESS)

    @admin.action(description="Отметить исправленными")
    def mark_resolved(self, request: HttpRequest, queryset: QuerySet[Report]) -> None:
        """Move the selected reports to RESOLVED."""
        self._set_status(request, queryset, ReportStatus.RESOLVED)

    @admin.action(description="Отклонить")
    def mark_rejected(self, request: HttpRequest, queryset: QuerySet[Report]) -> None:
        """Move the selected reports to REJECTED."""
        self._set_status(request, queryset, ReportStatus.REJECTED)
