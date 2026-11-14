# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the inline chord markup checks."""

from apps.songs.chord_text import find_chord_text_errors, find_unknown_chords


def test_find_chord_text_errors_accepts_well_formed_chords() -> None:
    chord_text = "###### Куплет  \r\nМы не [G (2)]знали друг друга до [C]этого [G]лета"

    assert find_chord_text_errors(chord_text) == []


def test_find_chord_text_errors_reports_unclosed_bracket() -> None:
    assert find_chord_text_errors("Холодный [Am ветер с дождём")


def test_find_chord_text_errors_reports_closing_bracket_without_opening() -> None:
    assert find_chord_text_errors("Холодный Am] ветер с дождём")


def test_find_chord_text_errors_reports_nested_brackets() -> None:
    assert find_chord_text_errors("Холодный [[Am]] ветер")


def test_find_chord_text_errors_reports_empty_brackets() -> None:
    assert find_chord_text_errors("Холодный [ ]ветер")


def test_find_chord_text_errors_reports_bracket_left_open_at_line_end() -> None:
    assert find_chord_text_errors("Белый снег, [Am\r\n]серый лёд")


def test_find_unknown_chords_ignores_performance_note_after_chord_name() -> None:
    assert find_unknown_chords("[G (2)]Город в [Dm(4)]петле", ["G", "Dm"]) == set()


def test_find_unknown_chords_keeps_slash_chord_whole() -> None:
    assert find_unknown_chords("[Am/D]Звезда", ["Am"]) == {"Am/D"}


def test_find_unknown_chords_reports_name_missing_from_known_titles() -> None:
    assert find_unknown_chords("[Fm#(8)]Солнце [Hm]", ["F#m", "Hm"]) == {"Fm#"}
