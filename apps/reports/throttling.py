# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Rate limiting for report submission."""

import hashlib
from collections.abc import Mapping

from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from apps.reports.constants import REPORT_DEVICE_THROTTLE_SCOPE


class ReportDeviceRateThrottle(SimpleRateThrottle):
    """Limit report submissions per device rather than per IP address.

    Mobile carriers put many subscribers behind one address (CGNAT), so a
    strict per-IP limit would reject people who sent a single report. The
    `device_id` is client-supplied and trivially rotated, so this limit only
    keeps one honest device from flooding the inbox; the looser per-IP limit
    applied alongside it is what bounds abuse. A request without a usable
    `device_id` is limited by its IP address instead.
    """

    scope = REPORT_DEVICE_THROTTLE_SCOPE

    def get_cache_key(self, request: Request, view: APIView) -> str:
        """Key the rate on the submitted device id, or on the IP without one."""
        data = request.data
        device_id = data.get("device_id") if isinstance(data, Mapping) else None
        if isinstance(device_id, str) and device_id:
            # The id is arbitrary client text; hashing keeps the key valid for
            # cache backends that restrict key length and characters.
            ident = hashlib.sha256(device_id.encode()).hexdigest()
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
