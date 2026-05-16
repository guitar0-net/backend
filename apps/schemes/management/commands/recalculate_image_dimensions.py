# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Management command to recalculate image dimensions for all image schemes."""

from django.core.management.base import BaseCommand

from apps.schemes.services import ImageSchemeService


class Command(BaseCommand):
    """Recalculate width and height for every ImageScheme from the actual file."""

    help = "Recalculate width and height for every ImageScheme from the actual file."

    def handle(self, *args: object, **options: object) -> None:
        """Read each image file and update the width/height fields in the database."""
        updated = ImageSchemeService.bulk_recalculate_dimensions()
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} image scheme(s)."))
