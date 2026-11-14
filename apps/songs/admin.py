# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Admin settings for songs."""

from typing import TYPE_CHECKING, ClassVar

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from markdownx.admin import MarkdownxModelAdmin  # type: ignore[import-untyped]

from apps.songs.chord_text import find_chord_text_errors, find_unknown_chords
from apps.songs.models import Song
from apps.songs.services import delete_song, delete_songs, save_song

if TYPE_CHECKING:
    _SongModelForm = forms.ModelForm[Song]
else:
    # ModelForm is generic only in django-stubs; at runtime it is not subscriptable.
    _SongModelForm = forms.ModelForm


class SongAdminForm(_SongModelForm):
    """Song form that rejects malformed chord brackets and an empty song."""

    class Meta:
        """Bind the form to every Song field."""

        model = Song
        fields = "__all__"

    def clean_chord_text(self) -> str:
        """Reject chord brackets that clients cannot cut out of the text."""
        chord_text: str = self.cleaned_data["chord_text"]
        errors = find_chord_text_errors(chord_text)
        if errors:
            raise forms.ValidationError(errors)
        return chord_text

    def clean(self) -> dict[str, object] | None:
        """Require the song to have at least one of the two texts."""
        cleaned_data = super().clean()
        if "chord_text" in self.errors:
            return cleaned_data
        if cleaned_data is not None and not (
            cleaned_data.get("text") or cleaned_data.get("chord_text")
        ):
            raise forms.ValidationError(
                "Заполните «Текст с аккордами» (или устаревший «Текст песни»)."
            )
        return cleaned_data


@admin.register(Song)
class SongAdmin(MarkdownxModelAdmin):  # type: ignore[misc]
    """Admin interface for the Song model."""

    form = SongAdminForm
    filter_horizontal = ("chords", "schemes")
    list_display = ("title", "metronome")
    list_editable = ("metronome",)
    fieldsets: ClassVar = (
        (None, {"fields": ("title", "metronome", "chord_text", "chords", "schemes")}),
        ("Устаревший текст", {"fields": ("text",), "classes": ("collapse",)}),
    )

    def save_model(  # noqa: PLR6301
        self,
        request: HttpRequest,
        obj: Song,
        form: forms.ModelForm[Song],
        change: bool,
    ) -> None:
        """Save the song and propagate the change timestamp to related lessons."""
        save_song(obj)

    def save_related(
        self,
        request: HttpRequest,
        form: forms.ModelForm[Song],
        formsets: list[forms.BaseFormSet[forms.Form]],
        change: bool,
    ) -> None:
        """Save the chords and schemes, then warn about chords the text misses.

        Runs after the many-to-many rows are written, so the check sees the
        chords just picked in the form. It only warns: the legacy notation is
        inconsistent (`Fm#` next to `F#m`), and blocking the save would stop
        editors on cosmetic mismatches.
        """
        super().save_related(request, form, formsets, change)
        song = form.instance
        unknown = find_unknown_chords(
            song.chord_text, song.chords.values_list("title", flat=True)
        )
        if unknown:
            self.message_user(
                request,
                "В тексте с аккордами есть аккорды, не привязанные к песне: "
                + ", ".join(sorted(unknown)),
                level=messages.WARNING,
                fail_silently=True,
            )

    def delete_model(self, request: HttpRequest, obj: Song) -> None:  # noqa: PLR6301
        """Delete a song and propagate the change to lessons that used it."""
        delete_song(obj)

    def delete_queryset(  # noqa: PLR6301
        self,
        request: HttpRequest,
        queryset: QuerySet[Song],
    ) -> None:
        """Delete the songs selected in the bulk action.

        Django does not route the bulk action through `delete_model`, so the
        propagation has to be repeated here or deleting from the changelist
        would leave every affected lesson stale.
        """
        delete_songs(queryset)
