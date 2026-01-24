# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""App configuration for the courses app."""

from django.apps import AppConfig


class CoursesConfig(AppConfig):
    """Configuration class for the courses Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.courses"
