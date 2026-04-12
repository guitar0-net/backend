# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Global pagination configuration."""

from rest_framework.pagination import LimitOffsetPagination


class GuitarPagination(LimitOffsetPagination):
    """Default pagination: 20 items per page, capped at 50."""

    default_limit = 20
    max_limit = 50
