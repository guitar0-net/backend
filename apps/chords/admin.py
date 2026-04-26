# SPDX-FileCopyrightText: 2025 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin settings for chords."""

from __future__ import annotations

from typing import Any, ClassVar

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.forms import ModelForm
from django.http import HttpRequest

from apps.chords.models import Chord, ChordPosition
from apps.chords.services import ChordService


class ChordPositionInline(admin.TabularInline):  # type: ignore[type-arg]
    """Admin interface for ChordPosition."""

    model = ChordPosition
    extra = 0
    fields = ("string_number", "fret", "finger")


@admin.register(Chord)
class ChordAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Admin interface for the Chord model."""

    list_display = ("title", "musical_title", "start_fret", "has_barre")
    list_filter = ("has_barre",)
    search_fields = ("title", "musical_title")
    ordering = ("order_in_note",)
    inlines: ClassVar[list[type[InlineModelAdmin[Any, Any]]]] = [ChordPositionInline]

    def save_related(
        self,
        request: HttpRequest,
        form: ModelForm[Chord],
        formsets: Any,  # noqa: ANN401
        change: bool,
    ) -> None:
        """Regenerate SVG fields after all inlines are saved."""
        super().save_related(request, form, formsets, change)
        ChordService.regenerate_svg(chord=form.instance)
