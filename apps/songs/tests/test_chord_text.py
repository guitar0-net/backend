# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the inline chord markup checks and rendering."""

from apps.songs.chord_text import (
    find_chord_text_errors,
    find_unknown_chords,
    render_chord_text_html,
)


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


def test_render_chord_text_html_puts_chord_name_in_bold() -> None:
    assert '<b class="chord-symbol">Am7</b>' in render_chord_text_html("Мы [Am7]шли")


def test_render_chord_text_html_separates_performance_note_from_name() -> None:
    html = render_chord_text_html("Мы не [G (2)]знали")

    assert '<span class="chord-note">(2)</span>' in html


def test_render_chord_text_html_puts_syllable_under_its_chord() -> None:
    html = render_chord_text_html("Город в [Dm(4)]петле")

    assert '<span class="chord-syllable">петле</span>' in html


def test_render_chord_text_html_keeps_word_with_mid_word_chord_unbreakable() -> None:
    html = render_chord_text_html("Звезда по имени Сол[C]нце")

    assert '<span class="chord-word">Сол<span class="chord-pair">' in html


def test_render_chord_text_html_gives_line_end_chord_a_blank_syllable() -> None:
    html = render_chord_text_html("Белый снег, серый лёд [Em]")

    assert '<span class="chord-syllable">&nbsp;</span>' in html


def test_render_chord_text_html_leaves_no_brackets_in_output() -> None:
    assert "[" not in render_chord_text_html("[Hm]Пачка [F#]сигарет")


def test_render_chord_text_html_escapes_markup_inside_chord() -> None:
    assert "<i>" not in render_chord_text_html("Кино [<i>]ночь")


def test_render_chord_text_html_renders_markdown_around_chords() -> None:
    html = render_chord_text_html("**Am G**  \nВ [Am]небе")

    assert "<strong>Am G</strong>" in html
