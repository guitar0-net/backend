# SPDX-FileCopyrightText: 2025 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the chords app."""

from django.db.models import QuerySet

from .models import Chord


def get_chord_by_id(chord_id: int) -> Chord | None:
    """Get a single Chord by ID with related data.

    Returns:
        Chord or None if not found.
    """
    return Chord.objects.filter(id=chord_id).prefetch_related("positions").first()


def get_all_chords() -> QuerySet[Chord]:
    """Get a QuerySet of all Chord objects with positions.

    Returns:
        QuerySet[Chord]: Optimized QuerySet of all chords ordered by
            order_in_note and title.
    """
    return (
        Chord.objects
        .all()
        .order_by("title", "order_in_note")
        .prefetch_related("positions")
    )
