# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Prometheus metrics for user reports, so new ones can raise an alert."""

from prometheus_client import Counter

from apps.ops.constants import METRIC_PREFIX
from apps.ops.registry import get_registry

reports_submitted_total = Counter(
    name=f"{METRIC_PREFIX}reports_submitted_total",
    documentation="User reports accepted (retried submissions are not counted).",
    labelnames=["target_type", "reason"],
    registry=get_registry(),
)

reports_target_missing_total = Counter(
    name=f"{METRIC_PREFIX}reports_target_missing_total",
    documentation=(
        "Accepted reports whose content item was not found. A steady rise "
        "points at a client sending wrong target ids rather than at deleted "
        "content."
    ),
    labelnames=["target_type"],
    registry=get_registry(),
)
