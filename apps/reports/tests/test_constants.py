# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for reports constants."""

from apps.reports.constants import (
    REASONS_BY_TARGET_TYPE,
    ReportReason,
    ReportTargetType,
)


def test_every_target_type_offers_reasons() -> None:
    assert set(REASONS_BY_TARGET_TYPE) == set(ReportTargetType.values)


def test_every_target_type_offers_the_other_reason_last() -> None:
    assert all(
        reasons[-1] == ReportReason.OTHER for reasons in REASONS_BY_TARGET_TYPE.values()
    )
