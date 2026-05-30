# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the sync app."""

import logging
from datetime import UTC, datetime
from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lessons.models import Lesson
from apps.sync.selectors import (
    get_content_version,
    get_course_lessons_for_sync,
    get_courses_for_sync,
    get_lessons_for_sync,
    get_published_course_uuids,
    get_published_lesson_uuids,
)

from .serializers.sync_serializers import (
    ChordSyncSerializer,
    CourseFlatSerializer,
    CourseLessonFlatSerializer,
    LessonFlatSerializer,
    SchemeSyncSerializer,
    SongFlatSerializer,
)

logger = logging.getLogger("sync")

_SINCE_PARAM = OpenApiParameter(
    name="since",
    type=str,
    location=OpenApiParameter.QUERY,
    description=(
        "ISO-8601 timestamp. When provided, only lessons updated after this "
        "point are included in `lessons`, `songs`, `chords`, and `schemes`. "
        "`lesson_uuids` always contains the full set of published UUIDs "
        "regardless of this parameter."
    ),
    required=False,
    examples=[],
)


@extend_schema(parameters=[_SINCE_PARAM])
class LessonsSyncView(APIView):
    """Flat sync payload for offline download.

    Returns a normalized response where each entity type is in its own
    top-level array (no nesting). Songs reference chords and schemes by ID.

    Delta sync: use `?since=<ISO-8601>` to receive only changed lessons and
    their associated songs/chords/schemes. `lesson_uuids` and `course_*`
    fields are always the complete published set regardless of `since`.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """Return flat sync payload."""
        since = self._parse_since(request)
        if since is None and "since" in request.query_params:
            return Response(
                {"detail": "Invalid `since` value — expected ISO-8601 datetime."},
                status=400,
            )

        lessons_qs = get_lessons_for_sync(since)
        lessons_list = list(lessons_qs)

        lessons_data = LessonFlatSerializer(lessons_list, many=True).data
        songs_data, chords_data, schemes_data = self._build_flat_song_data(lessons_list)

        courses_qs = get_courses_for_sync()
        courses_data = CourseFlatSerializer(courses_qs, many=True).data

        course_lessons_qs = get_course_lessons_for_sync()
        course_lessons_data = CourseLessonFlatSerializer(
            course_lessons_qs, many=True
        ).data

        logger.debug(
            "Sync: since=%s lessons=%d songs=%d chords=%d schemes=%d",
            since,
            len(lessons_data),
            len(songs_data),
            len(chords_data),
            len(schemes_data),
        )

        return Response({
            "version": get_content_version(),
            "lesson_uuids": [str(u) for u in get_published_lesson_uuids()],
            "lessons": lessons_data,
            "songs": songs_data,
            "chords": chords_data,
            "schemes": schemes_data,
            "course_uuids": [str(u) for u in get_published_course_uuids()],
            "courses": courses_data,
            "course_lessons": course_lessons_data,
        })

    @staticmethod
    def _build_flat_song_data(
        lessons: list[Lesson],
    ) -> tuple[Any, Any, Any]:
        """Extract flat songs, deduplicated chords, and deduplicated schemes.

        Iterates over prefetched songs/chords/schemes — no extra DB queries.
        Returns (songs_data, chords_data, schemes_data) ready for serialization.
        A song shared across multiple lessons appears once per lesson with a
        different lesson_uuid — intentional, mirrors the M2M relationship.
        """
        songs_out: list[dict[str, Any]] = []
        chord_map: dict[int, Any] = {}
        scheme_map: dict[int, Any] = {}

        for lesson in lessons:
            for song in lesson.songs.all():
                song_chords = list(song.chords.all())
                song_schemes = list(song.schemes.all())
                songs_out.append({
                    "uuid": song.uuid,
                    "lesson_uuid": lesson.uuid,
                    "title": song.title,
                    "text": song.text,
                    "metronome": song.metronome,
                    "chord_ids": [c.pk for c in song_chords],
                    "scheme_ids": [s.pk for s in song_schemes],
                })
                for c in song_chords:
                    chord_map.setdefault(c.pk, c)
                for s in song_schemes:
                    scheme_map.setdefault(s.pk, s)

        songs_data = SongFlatSerializer(songs_out, many=True).data
        chords_data = ChordSyncSerializer(list(chord_map.values()), many=True).data
        schemes_data = SchemeSyncSerializer(list(scheme_map.values()), many=True).data
        return songs_data, chords_data, schemes_data

    @staticmethod
    def _parse_since(request: Request) -> datetime | None:
        """Parse the ?since= query param.

        Returns None if the param is absent (not an error).
        Returns None if the param is present but invalid (caller checks
        `"since" in request.query_params` to distinguish the two cases).
        """
        raw = request.query_params.get("since")
        if raw is None:
            return None
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return None
        else:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt


class ContentVersionView(APIView):
    """Lightweight endpoint for staleness checks.

    The client calls this on app launch. If `version` matches the locally
    stored value, no sync is needed. Only when it differs does the client
    call `LessonsSyncView`.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:  # noqa: PLR6301
        """Return current content version."""
        return Response({"version": get_content_version()})
