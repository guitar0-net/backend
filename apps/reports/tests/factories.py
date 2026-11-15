# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factories for generating test reports instances."""

from factory import Faker  # type: ignore[attr-defined]
from factory.django import DjangoModelFactory

from apps.reports.constants import (
    ClientPlatform,
    ReportReason,
    ReportStatus,
    ReportTargetType,
)
from apps.reports.models import Report


class ReportFactory(DjangoModelFactory[Report]):
    """Factory for creating Report instances about the app itself."""

    target_type = ReportTargetType.APP
    target_id = ""
    reason = ReportReason.BUG
    message = Faker("sentence", locale="ru_RU")
    device_id = Faker("uuid4")
    platform = ClientPlatform.ANDROID
    app_version = Faker("numerify", text="#.#.#")
    status = ReportStatus.NEW

    class Meta:
        model = Report
