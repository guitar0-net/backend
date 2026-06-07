# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs utilities."""

from apps.songs.utils import transliterate_for_filename


def test_transliterate_cyrillic_to_latin() -> None:
    assert transliterate_for_filename("Звёздочка") == "Zvyozdochka"


def test_transliterate_spaces_become_underscores() -> None:
    assert transliterate_for_filename("Во поле берёза") == "Vo_pole_beryoza"


def test_transliterate_mixed_latin_and_cyrillic() -> None:
    assert transliterate_for_filename("AC DC Рок") == "AC_DC_Rok"


def test_transliterate_collapses_multiple_spaces() -> None:
    assert transliterate_for_filename("Слово  два") == "Slovo_dva"


def test_transliterate_special_chars_become_underscores() -> None:
    assert transliterate_for_filename("Пе$сня!") == "Pe_snya"


def test_transliterate_unknown_unicode_becomes_underscore() -> None:
    assert transliterate_for_filename("Рок★ролл") == "Rok_roll"


def test_transliterate_soft_sign_is_removed() -> None:
    assert transliterate_for_filename("День") == "Den"


def test_transliterate_hard_sign_is_removed() -> None:
    assert transliterate_for_filename("Объект") == "Obekt"


def test_transliterate_hyphen_is_preserved() -> None:
    assert transliterate_for_filename("Иван-царевич") == "Ivan-tsarevich"


def test_transliterate_empty_string_returns_fallback() -> None:
    assert transliterate_for_filename("") == "song"


def test_transliterate_only_special_chars_returns_fallback() -> None:
    assert transliterate_for_filename("!!!") == "song"


def test_transliterate_uppercase_preserved() -> None:
    assert transliterate_for_filename("ПРИВЕТ") == "PRIVET"


def test_transliterate_latin_title_unchanged() -> None:
    assert transliterate_for_filename("Hotel California") == "Hotel_California"
