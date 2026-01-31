# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Prometheus metrics application.

This module provides the public API for metrics. Other applications should
import metrics from here rather than using prometheus_client directly.
"""

from .registry import get_registry, reset_registry
