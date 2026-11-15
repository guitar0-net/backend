# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""App configuration for the reports application."""

from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Configuration class for the reports Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    verbose_name = "Обратная связь"
