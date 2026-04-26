# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Management command to regenerate SVG diagrams for all chords."""

from django.core.management.base import BaseCommand

from apps.chords.models import Chord
from apps.chords.svg_renderer import render_chord_svg


class Command(BaseCommand):
    """Regenerate SVG diagrams for all existing chords."""

    help = "Regenerate svg_horizontal and svg_vertical for every Chord in the database."

    def handle(self, *args: object, **options: object) -> None:
        """Iterate all chords and regenerate their SVG fields."""
        chords = Chord.objects.prefetch_related("positions").all()
        updated = 0
        for chord in chords:
            chord.svg_horizontal, chord.svg_vertical = render_chord_svg(chord)
            updated += 1
        Chord.objects.bulk_update(chords, ["svg_horizontal", "svg_vertical"])
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} chord(s)."))
