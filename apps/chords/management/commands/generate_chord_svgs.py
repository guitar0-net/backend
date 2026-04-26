# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Management command to regenerate SVG diagrams for all chords."""

from django.core.management.base import BaseCommand

from apps.chords.services import ChordService


class Command(BaseCommand):
    """Regenerate SVG diagrams for all existing chords."""

    help = "Regenerate svg_horizontal and svg_vertical for every Chord in the database."

    def handle(self, *args: object, **options: object) -> None:
        """Iterate all chords and regenerate their SVG fields."""
        updated = ChordService.bulk_regenerate_svgs()
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} chord(s)."))
