# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the songs API v1."""

import logging
import uuid as uuid_module

from django.http import Http404, HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.songs.pdf_renderer import PrintSettings, render_song_pdf
from apps.songs.selectors import get_song_by_uuid
from apps.songs.utils import transliterate_for_filename

from .serializers.song_print_settings_serializer import SongPrintSettingsSerializer

logger = logging.getLogger("songs")


class SongPrintView(APIView):
    """Generate and return a printable PDF for a song."""

    permission_classes = (AllowAny,)

    def post(self, request: Request, uuid: uuid_module.UUID) -> HttpResponse:  # noqa: PLR6301
        """Accept print settings and return the song as a PDF document."""
        song = get_song_by_uuid(uuid)
        if song is None:
            logger.warning("Song not found for print: uuid=%s", uuid)
            raise Http404

        serializer = SongPrintSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        settings = PrintSettings(
            show_chords=data["show_chords"],
            show_schemes=data["show_schemes"],
            show_text=data["show_text"],
            chord_orientation=data["chord_orientation"],
            chord_size=data["chord_size"],
            scheme_size=data["scheme_size"],
            text_size=data["text_size"],
            columns_count=data["columns_count"],
        )
        pdf_bytes = render_song_pdf(song, settings)

        filename = f"{transliterate_for_filename(song.title)}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
