# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the chords app."""

import logging

from django.db.models import QuerySet
from django.http import Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.chords.models import Chord
from apps.chords.selectors import get_all_chords, get_chord_by_id

from .serializers.chord_detail_serializer import ChordDetailSerializer
from .serializers.chords_list_serializer import ChordsListSerializer

logger = logging.getLogger("chords")


class ChordsListView(ListAPIView[Chord]):
    """List all chords."""

    permission_classes = (AllowAny,)
    serializer_class = ChordsListSerializer

    def get_queryset(self) -> QuerySet[Chord]:  # noqa: PLR6301
        """Return chords queryset."""
        logger.debug("Fetching chords list")
        return get_all_chords()


class ChordDetailView(RetrieveAPIView[Chord]):
    """Retrieve a single chord by ID."""

    permission_classes = (AllowAny,)
    serializer_class = ChordDetailSerializer

    def get_object(self) -> Chord:
        """Return chord by ID or raise 404."""
        chord_id = self.kwargs["pk"]
        chord = get_chord_by_id(chord_id)
        if chord is None:
            logger.warning("Chord not found: id=%s", chord_id)
            raise Http404
        logger.debug("Fetched chord: id=%s, title=%s", chord_id, chord.title)
        return chord
