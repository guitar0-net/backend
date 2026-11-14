# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Checks for the inline chord markup of `Song.chord_text`.

A chord is written in square brackets right before the syllable it belongs
to: `Мы не [G (2)]знали`. Anything after the chord name inside the brackets
(a space or an opening parenthesis onwards) is a performance note such as a
strum count, so only the leading name is compared with the song's chords.
"""

import re
from collections.abc import Iterable

_CHORD_PATTERN = re.compile(r"\[([^\[\]]*)\]")
_CHORD_NAME_END = re.compile(r"[\s(]")


def find_chord_text_errors(chord_text: str) -> list[str]:
    """Return a description of every malformed chord bracket, by line number.

    Clients cut the chords out before rendering markdown, so a stray bracket
    would swallow lyrics or leak into the rendered text.
    """
    errors: list[str] = []
    for number, line in enumerate(chord_text.splitlines(), start=1):
        is_open = False
        for char in line:
            if char == "[" and is_open:
                errors.append(f"Строка {number}: вложенная «[».")
            elif char == "]" and not is_open:
                errors.append(f"Строка {number}: «]» без открывающей «[».")
            if char in "[]":
                is_open = char == "["
        if is_open:
            errors.append(f"Строка {number}: «[» не закрыта.")
        if any(not chord.strip() for chord in _CHORD_PATTERN.findall(line)):
            errors.append(f"Строка {number}: пустые скобки «[]».")
    return errors


def find_unknown_chords(chord_text: str, known_titles: Iterable[str]) -> set[str]:
    """Return chord names used in the text that are not among `known_titles`."""
    known = set(known_titles)
    names = {
        _CHORD_NAME_END.split(chord.strip(), maxsplit=1)[0]
        for chord in _CHORD_PATTERN.findall(chord_text)
    }
    return {name for name in names if name and name not in known}
